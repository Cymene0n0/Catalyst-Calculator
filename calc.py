import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
import re
from datetime import datetime

# ==================== 1. 核心纠错与格式化引擎 ====================

def smart_format_formula(text):
    """智能将普通化学式转换为含下标的标准格式"""
    if not text: return ""
    text = text.replace('.', '·').replace('*', '·')
    sub_map = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
               '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}

    if '·' in text:
        parts = text.split('·')
        main_part = "".join(sub_map.get(c, c) if c.isdigit() else c for c in parts[0])
        res_hydrate = []
        for p in parts[1:]:
            match = re.match(r'^(\d+)(.*)$', p.strip())
            if match:
                coeff = match.group(1) 
                mol = "".join(sub_map.get(c, c) if c.isdigit() else c for c in match.group(2))
                res_hydrate.append(f"{coeff}{mol}")
            else:
                res_hydrate.append("".join(sub_map.get(c, c) if c.isdigit() else c for c in p))
        return f"{main_part}·" + "·".join(res_hydrate)

    return "".join(sub_map.get(c, c) if c.isdigit() else c for c in text)

# ==================== 2. 数据库管理 ====================

class ElementInfo:
    def __init__(self, filename="element_db.json"):
        self.filename = filename
        # 全量原子质量 (精确至 0.001)
        self.mass_data = {
            'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.811, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180,
            'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078,
            'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.380,
            'Ga': 69.723, 'Ge': 72.630, 'As': 74.922, 'Se': 78.960, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.468, 'Sr': 87.620, 'Y': 88.906, 'Zr': 91.224,
            'Nb': 92.906, 'Mo': 95.960, 'Tc': 98.000, 'Ru': 101.070, 'Rh': 102.906, 'Pd': 106.420, 'Ag': 107.868, 'Cd': 112.411, 'In': 114.818, 'Sn': 118.710,
            'Sb': 121.760, 'Te': 127.600, 'I': 126.904, 'Xe': 131.293, 'Cs': 132.905, 'Ba': 137.327, 'La': 138.905, 'Ce': 140.116, 'Pr': 140.908, 'Nd': 144.242,
            'Pm': 145.000, 'Sm': 150.360, 'Eu': 151.964, 'Gd': 157.250, 'Tb': 158.925, 'Dy': 162.500, 'Ho': 164.930, 'Er': 167.259, 'Tm': 168.934, 'Yb': 173.054,
            'Lu': 174.967, 'Hf': 178.490, 'Ta': 180.948, 'W': 183.840, 'Re': 186.207, 'Os': 190.230, 'Ir': 192.217, 'Pt': 195.084, 'Au': 196.967, 'Hg': 200.592,
            'Tl': 204.383, 'Pb': 207.200, 'Bi': 208.980, 'Po': 209.000, 'At': 210.000, 'Rn': 222.000, 'Fr': 223.000, 'Ra': 226.000, 'Ac': 227.000, 'Th': 232.038,
            'Pa': 231.036, 'U': 238.029, 'Np': 237.000, 'Pu': 244.000, 'Am': 243.000, 'Cm': 247.000, 'Bk': 247.000, 'Cf': 251.000, 'Es': 252.000, 'Fm': 257.000,
            'Md': 258.000, 'No': 259.000, 'Lr': 262.000, 'Rf': 267.000, 'Db': 270.000, 'Sg': 271.000, 'Bh': 270.000, 'Hs': 277.000, 'Mt': 276.000, 'Ds': 281.000,
            'Rg': 280.000, 'Cn': 285.000, 'Nh': 284.000, 'Fl': 289.000, 'Mc': 288.000, 'Lv': 293.000, 'Ts': 294.000, 'Og': 294.000
        }
        self.name_map = {
            'H':'氢','He':'氦','Li':'锂','Be':'铍','B':'硼','C':'碳','N':'氮','O':'氧','F':'氟','Ne':'氖',
            'Na':'钠','Mg':'镁','Al':'铝','Si':'硅','P':'磷','S':'硫','Cl':'氯','Ar':'氩','K':'钾','Ca':'钙',
            'Sc':'钪','Ti':'钛','V':'钒','Cr':'铬','Mn':'锰','Fe':'铁','Co':'钴','Ni':'镍','Cu':'铜','Zn':'锌',
            'Ga':'镓','Ge':'锗','As':'砷','Se':'硒','Br':'溴','Kr':'氪','Rb':'铷','Sr':'锶','Y':'钇','Zr':'锆',
            'Nb':'铌','Mo':'钼','Tc':'锝','Ru':'钌','Rh':'铑','Pd':'钯','Ag':'银','Cd':'镉','In':'铟','Sn':'锡',
            'Sb':'锑','Te':'碲','I':'碘','Xe':'氙','Cs':'铯','Ba':'钡','La':'镧','Ce':'铈','Pr':'镨','Nd':'钕',
            'Pm':'钷','Sm':'钐','Eu':'铕','Gd':'钆','Tb':'铽','Dy':'镝','Ho':'钬','Er':'铒','Tm':'铥','Yb':'镱',
            'Lu':'镥','Hf':'铪','Ta':'钽','W':'钨','Re':'铼','Os':'锇','Ir':'铱','Pt':'铂','Au':'金','Hg':'汞',
            'Tl':'铊','Pb':'铅','Bi':'铋','Po':'钋','At':'砹','Rn':'氡','Fr':'钫','Ra':'镭','Ac':'锕','Th':'钍',
            'Pa':'镤','U':'铀','Np':'镎','Pu':'钚','Am':'镅','Cm':'锔','Bk':'锫','Cf':'锎','Es':'锿','Fm':'镄',
            'Md':'钔','No':'锘','Lr':'铹','Rf':'𬬻','Db':'𬭊','Sg':'𬭳','Bh':'𬭛','Hs':'𬭶','Mt':'鿏','Ds':'𫟼',
            'Rg':'𬬭','Cn':'鎶','Nh':'鿭','Fl':'𫓧','Mc':'镆','Lv':'𫟷','Ts':'𫑼','Og':'𬭯'
        }
        self.elements = self.get_initial_db()
        self.load_custom_data()

    def get_initial_db(self):
        raw_compounds = {
            'Mg': [('MgO', 40.304), ('Mg(OH)2', 58.320), ('Mg(NO3)2', 148.315), ('Mg(NO3)2·6H2O', 256.407), ('MgCO3', 84.314)],
            'Al': [('Al2O3', 101.961), ('Al(OH)3', 78.004), ('Al(NO3)3', 212.996), ('Al(NO3)3·9H2O', 375.134)],
            'Fe': [('Fe2O3', 159.688), ('Fe3O4', 231.533), ('Fe(OH)3', 106.867), ('Fe(NO3)3·9H2O', 403.999)],
            'Cu': [('CuO', 79.545), ('Cu2O', 143.091), ('Cu(OH)2', 97.561), ('Cu(NO3)2·3H2O', 241.602)],
            'Li': [('Li2O', 29.881), ('LiOH', 23.948), ('LiNO3', 68.946)],
            'Na': [('Na2O', 61.979), ('NaOH', 39.997), ('NaNO3', 84.995), ('Na2CO3', 105.988)],
            'Co': [('Co3O4', 240.797), ('Co(OH)2', 92.948), ('Co(NO3)2·6H2O', 291.035)],
            'Ni': [('NiO', 74.692), ('Ni(OH)2', 92.708), ('Ni(NO3)2·6H2O', 290.795)],
            'La': [('La2O3', 325.809), ('La(OH)3', 189.917), ('La(NO3)3·6H2O', 433.012)],
            'Ag': [('Ag2O', 231.735), ('AgNO3', 169.873)],
        }
        db = {}
        for sym, mass in self.mass_data.items():
            comps = []
            if sym in raw_compounds:
                for formula, c_mass in raw_compounds[sym]:
                    comps.append((smart_format_formula(formula), round(c_mass, 3)))
            db[sym] = {'name': self.name_map.get(sym, sym), 'mass': round(mass, 3), 'compounds': comps}
        return db

    def load_custom_data(self):
        if os.path.exists("element_db.json"):
            try:
                with open("element_db.json", 'r', encoding='utf-8') as f:
                    custom = json.load(f)
                    for k, v in custom.items():
                        if k in self.elements: self.elements[k].update(v)
            except: pass

    def save_custom_data(self):
        with open("element_db.json", 'w', encoding='utf-8') as f:
            json.dump(self.elements, f, ensure_ascii=False, indent=2)

# ==================== 3. 周期表 UI ====================

class PeriodicTableWindow(tk.Toplevel):
    def __init__(self, parent, db, callback):
        super().__init__(parent); self.title("元素周期表"); self.geometry("1150x920")
        self.db = db; self.callback = callback; self.current_symbol = None; self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=10); main_frame.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style(); style.configure("Table.Treeview", rowheight=35, font=('微软雅黑', 10))

        pts = [(1,1,"H"),(1,18,"He"),(2,1,"Li"),(2,2,"Be"),(2,13,"B"),(2,14,"C"),(2,15,"N"),(2,16,"O"),(2,17,"F"),(2,18,"Ne"),
               (3,1,"Na"),(3,2,"Mg"),(3,13,"Al"),(3,14,"Si"),(3,15,"P"),(3,16,"S"),(3,17,"Cl"),(3,18,"Ar"),
               (4,1,"K"),(4,2,"Ca"),(4,3,"Sc"),(4,4,"Ti"),(4,5,"V"),(4,6,"Cr"),(4,7,"Mn"),(4,8,"Fe"),(4,9,"Co"),(4,10,"Ni"),(4,11,"Cu"),(4,12,"Zn"),(4,13,"Ga"),(4,14,"Ge"),(4,15,"As"),(4,16,"Se"),(4,17,"Br"),(4,18,"Kr"),
               (5,1,"Rb"),(5,2,"Sr"),(5,3,"Y"),(5,4,"Zr"),(5,5,"Nb"),(5,6,"Mo"),(5,7,"Tc"),(5,8,"Ru"),(5,9,"Rh"),(5,10,"Pd"),(5,11,"Ag"),(5,12,"Cd"),(5,13,"In"),(5,14,"Sn"),(5,15,"Sb"),(5,16,"Te"),(5,17,"I"),(5,18,"Xe"),
               (6,1,"Cs"),(6,2,"Ba"),(6,3,"*"),(6,4,"Hf"),(6,5,"Ta"),(6,6,"W"),(6,7,"Re"),(6,8,"Os"),(6,9,"Ir"),(6,10,"Pt"),(6,11,"Au"),(6,12,"Hg"),(6,13,"Tl"),(6,14,"Pb"),(6,15,"Bi"),(6,16,"Po"),(6,17,"At"),(6,18,"Rn"),
               (7,1,"Fr"),(7,2,"Ra"),(7,3,"#"),(7,4,"Rf"),(7,5,"Db"),(7,6,"Sg"),(7,7,"Bh"),(7,8,"Hs"),(7,9,"Mt"),(7,10,"Ds"),(7,11,"Rg"),(7,12,"Cn"),(7,13,"Nh"),(7,14,"Fl"),(7,15,"Mc"),(7,16,"Lv"),(7,17,"Ts"),(7,18,"Og")]
        for r, c, s in pts: self.make_btn(main_frame, r, c, s)

        for i, s in enumerate(["La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu"]): self.make_btn(main_frame, 9, i+4, s)
        for i, s in enumerate(["Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr"]): self.make_btn(main_frame, 10, i+4, s)

        detail_frame = ttk.LabelFrame(main_frame, text=" 物质数据详情 (保留3位小数) ", padding=10)
        detail_frame.grid(row=11, column=1, columnspan=18, sticky="nsew", pady=15)
        self.tree = ttk.Treeview(detail_frame, columns=("f", "m"), show='headings', height=8, style="Table.Treeview")
        self.tree.heading("f", text="物质化学式"); self.tree.heading("m", text="相对质量 (g/mol)"); self.tree.column("f", width=400); self.tree.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        op_panel = ttk.Frame(detail_frame); op_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cur_lab = tk.Label(op_panel, text="请点击元素按钮", font=('微软雅黑', 14, 'bold'), fg="#C0392B"); self.cur_lab.pack(anchor=tk.W, pady=5)
        
        btn_box = ttk.Frame(op_panel); btn_box.pack(fill=tk.X, pady=10)
        ttk.Button(btn_box, text=" 填入 Mx (活性) ", command=lambda: self.fill('mx')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_box, text=" 填入 Mz (前驱体) ", command=lambda: self.fill('mz')).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_box, text=" 删除选中行 ", command=self.delete_comp).pack(side=tk.LEFT, padx=2)
        
        self.add_box = ttk.Entry(op_panel); self.add_box.pack(fill=tk.X, pady=5)
        ttk.Button(op_panel, text="保存至本地数据库", command=self.add_comp).pack(anchor=tk.E)

    def make_btn(self, p, r, c, s):
        if s in ["*", "#"]: tk.Label(p, text=s).grid(row=r, column=c); return
        b = tk.Button(p, text=s, width=5, font=('Arial', 9, 'bold'), bg="#ECF0F1", relief="ridge", command=lambda: self.on_click(s)); b.grid(row=r, column=c, padx=1, pady=1)

    def on_click(self, s):
        self.current_symbol = s
        name = self.db.elements[s]['name']
        self.cur_lab.config(text=f"当前选中元素：{s}（{name}）")
        for i in self.tree.get_children(): self.tree.delete(i)
        atom_mass = f"{self.db.elements[s]['mass']:.3f}"
        self.tree.insert("", tk.END, values=(s, atom_mass), tags=('atom',))
        for f, m in self.db.elements[s].get('compounds', []):
            self.tree.insert("", tk.END, values=(f, f"{m:.3f}"))

    def add_comp(self):
        if not self.current_symbol: return
        raw = self.add_box.get()
        if ',' not in raw: messagebox.showerror("格式错误", "示例：CuO, 79.545"); return
        try:
            f_raw, m = raw.split(',')
            std_formula = smart_format_formula(f_raw.strip())
            self.db.elements[self.current_symbol]['compounds'].append((std_formula, round(float(m.strip()), 3)))
            self.db.save_custom_data(); self.on_click(self.current_symbol); self.add_box.delete(0, tk.END)
        except: messagebox.showerror("错误", "质量必须为数字")

    def delete_comp(self):
        sel = self.tree.selection()
        if not sel or 'atom' in self.tree.item(sel[0], 'tags'): return
        f = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("确认", f"确定删除 {f} 吗？"):
            self.db.elements[self.current_symbol]['compounds'] = [c for c in self.db.elements[self.current_symbol]['compounds'] if c[0] != f]
            self.db.save_custom_data(); self.on_click(self.current_symbol)

    def fill(self, target):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        self.callback(target, item[0], item[1])

# ==================== 4. 主计算界面 ====================

class CatalystCalculator:
    def __init__(self, root):
        self.root = root; self.root.title("负载型催化剂计算器 Pro"); self.root.geometry("1050x920")
        self.db = ElementInfo(); self.history = self.load_hist(); self.selected_names = {"mx": "-", "mz": "-"}
        self.setup_ui(); self.update_history()

    def setup_ui(self):
        top = ttk.LabelFrame(self.root, text=" 核心参数输入 ", padding=20); top.pack(fill=tk.X, padx=25, pady=15)
        self.entries = {}
        fields = [("负载量 (wt.%)", "loading", "如: 7.0"), ("载体质量 (g)", "support", "如: 10.0"), 
                  ("活性组分 Mx (g/mol)", "mx", "周期表选择"), ("前驱体 Mz (g/mol)", "mz", "周期表选择")]
        for i, (lab, key, tip) in enumerate(fields):
            ttk.Label(top, text=lab).grid(row=0, column=i*2, padx=5)
            e = PlaceholderEntry(top, placeholder=tip, width=15); e.grid(row=0, column=i*2+1, padx=5); self.entries[key] = e
        
        # --- 按钮栏：计算按钮单独放右边且醒目 ---
        ctrl = ttk.Frame(self.root); ctrl.pack(fill=tk.X, padx=25, pady=10)
        
        # 左侧辅助按钮
        ttk.Button(ctrl, text=" 📊 打开元素周期表 ", command=self.open_pt).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text=" 🔄 重置输入 ", command=self.reset).pack(side=tk.LEFT, padx=5)
        
        # 右侧核心计算按钮 (使用醒目的深蓝色样式)
        self.calc_btn = tk.Button(
            ctrl, 
            text=" 🧮 立即计算结果并复制 ", 
            command=self.calc,
            bg="#1F618D", fg="white",       # 深蓝色背景，白色字
            activebackground="#2E86C1",     # 点击时的颜色
            activeforeground="white",
            font=('微软雅黑', 12, 'bold'),     # 字号加大加粗
            relief="raised",                # 凸起效果
            cursor="hand2",                 # 鼠标手型
            padx=25, pady=8                 # 增加内边距使其更大
        )
        self.calc_btn.pack(side=tk.RIGHT, padx=5)

        self.res_str = tk.StringVar(value="所需前驱体质量：-- g")
        tk.Label(self.root, textvariable=self.res_str, font=('微软雅黑', 22, 'bold'), fg="#2980B9").pack(pady=15)

        # 历史记录区域
        hist_frame = ttk.LabelFrame(self.root, text=" 计算历史记录 ", padding=10); hist_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)
        
        hist_tool = ttk.Frame(hist_frame); hist_tool.pack(fill=tk.X, pady=5)
        ttk.Button(hist_tool, text=" 📥 导出成 Excel (CSV) ", command=self.export_to_xls).pack(side=tk.LEFT, padx=5)
        ttk.Button(hist_tool, text=" 🗑️ 删除选中记录 ", command=self.delete_history_item).pack(side=tk.LEFT, padx=5)
        ttk.Label(hist_tool, text="*提示：双击或选中后点击删除", font=('微软雅黑', 8), foreground="gray").pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(hist_frame, columns=("t","l","s","mx_n","mz_n","r"), show='headings', height=10)
        heads = [("t","时间",160),("l","负载量",90),("s","载体(g)",90),("mx_n","Mx(物质)",180),("mz_n","Mz(物质)",180),("r","结果(g)",110)]
        for cid, txt, wid in heads: self.tree.heading(cid, text=txt); self.tree.column(cid, width=wid)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(hist_frame, command=self.tree.yview); vsb.pack(side=tk.RIGHT, fill=tk.Y); self.tree.config(yscrollcommand=vsb.set)

        bot = ttk.Frame(self.root, padding=10); bot.pack(fill=tk.X)
        tk.Label(bot, text="Version 2026.4 | 布局优化：计算按钮置右且醒目", font=('微软雅黑', 9), fg="gray").pack(side=tk.LEFT)

    def load_hist(self):
        if os.path.exists("calc_history.json"):
            try:
                with open("calc_history.json", 'r', encoding='utf-8') as f: return json.load(f)
            except: return []
        return []

    def open_pt(self): PeriodicTableWindow(self.root, self.db, self.fill_entry)
    
    def fill_entry(self, key, formula, val):
        self.selected_names[key] = str(formula)
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, f"{float(val):.3f}")
        self.entries[key].config(fg='black'); self.entries[key].is_placeholder = False

    def calc(self):
        try:
            l = float(self.entries['loading'].get_val()); s = float(self.entries['support'].get_val())
            mx = float(self.entries['mx'].get_val()); mz = float(self.entries['mz'].get_val())
            ans = (s / (1 - l/100) - s) / (mx / mz); ans_s = f"{ans:.3f}"
            self.res_str.set(f"所需前驱体质量：{ans_s} g"); self.root.clipboard_clear(); self.root.clipboard_append(ans_s)
            
            mx_n = self.selected_names['mx'] if self.entries['mx'].get() == f"{mx:.3f}" else "手动"
            mz_n = self.selected_names['mz'] if self.entries['mz'].get() == f"{mz:.3f}" else "手动"
            
            self.history.insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inputs": {'loading':f"{l}%", 'support':f"{s:.3f}", 'mx':f"{mx:.3f}", 'mz':f"{mz:.3f}", 'mx_name': mx_n, 'mz_name': mz_n},
                "results": {'precursor_mass':ans_s}
            })
            self.save_history(); self.update_history()
        except: messagebox.showerror("错误", "请检查输入数据是否完整且有效")

    def save_history(self):
        with open("calc_history.json", 'w', encoding='utf-8') as f:
            json.dump(self.history[:500], f, ensure_ascii=False)

    def update_history(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.history:
            i = r['inputs']
            self.tree.insert("", tk.END, values=(r['timestamp'], i['loading'], i['support'], 
                                               f"{i['mx_name']}({i['mx']})", f"{i['mz_name']}({i['mz']})", 
                                               r['results']['precursor_mass']))

    def delete_history_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先在下方列表中选择一条记录")
            return
        if messagebox.askyesno("确认删除", "确定要永久删除这条记录吗？"):
            idx = self.tree.index(sel[0])
            if idx < len(self.history):
                del self.history[idx]
                self.save_history()
                self.update_history()

    def export_to_xls(self):
        if not self.history:
            messagebox.showwarning("导出失败", "历史记录为空")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Excel 兼容 CSV", "*.csv")],
            initialfilename=f"催化剂记录_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["时间", "负载量", "载体质量(g)", "活性组分(Mx)", "前驱体(Mz)", "所需质量(g)"])
                    for r in self.history:
                        i = r['inputs']
                        writer.writerow([r['timestamp'], i['loading'], i['support'], f"{i['mx_name']}({i['mx']})", f"{i['mz_name']}({i['mz']})", r['results']['precursor_mass']])
                messagebox.showinfo("成功", "导出成功")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

    def reset(self):
        for e in self.entries.values(): e.delete(0, tk.END); e._add_placeholder(None)
        self.selected_names = {"mx": "-", "mz": "-"}; self.res_str.set("所需前驱体质量：-- g")

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs); self.placeholder = placeholder; self.is_placeholder = True; self.config(fg='grey')
        self.insert(0, self.placeholder); self.bind("<FocusIn>", self._clear); self.bind("<FocusOut>", self._add)
    def _clear(self, e):
        if self.is_placeholder: self.delete(0, tk.END); self.config(fg='black'); self.is_placeholder = False
    def _add(self, e):
        if not self.get(): self._add_placeholder(None)
    def _add_placeholder(self, e):
        self.delete(0, tk.END); self.insert(0, self.placeholder); self.config(fg='grey'); self.is_placeholder = True
    def get_val(self): return "0" if self.is_placeholder else self.get()

if __name__ == "__main__":
    root = tk.Tk(); style = ttk.Style(); style.theme_use('clam'); app = CatalystCalculator(root); root.mainloop()