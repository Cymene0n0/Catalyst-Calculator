import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import csv
from datetime import datetime

class HistoryManager:
    """历史记录管理器"""
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = []
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_record(self, inputs, results):
        """添加记录"""
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "inputs": inputs,
            "results": results
        }
        self.history.append(record)
        # 只保留最近100条记录
        if len(self.history) > 100:
            self.history = self.history[-100:]
        self.save_history()
    
    def get_history(self):
        """获取所有历史记录"""
        return self.history.copy()
    
    def export_to_excel(self, filename=None):
        """导出历史记录到CSV/XLS格式"""
        if not filename:
            filename = f"催化剂计算历史_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # 写入标题行
                writer.writerow(['时间', '负载量(wt.%)', '载体质量(g)', '活性组分分子量(Mx)', 
                                '前驱体分子量(Mz)', 'f(质量分数)', '活性组分质量(g)', 
                                '成品总质量(g)', '制后总质量(g)', '所需前驱体质量(g)'])
                
                # 写入数据
                for record in self.history:
                    inputs = record.get('inputs', {})
                    results = record.get('results', {})
                    writer.writerow([
                        record.get('timestamp', ''),
                        inputs.get('loading', 0),
                        inputs.get('support', 0),
                        inputs.get('mx', 0),
                        inputs.get('mz', 0),
                        results.get('f', 0),
                        results.get('mx_mass', 0),
                        results.get('total_finished', 0),
                        results.get('total_after', 0),
                        results.get('precursor_mass', 0)
                    ])
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

class ElementInfo:
    """元素信息数据库"""
    def __init__(self):
        # 常见元素及其化合物信息
        self.elements = {
            'H': {'name': '氢', 'mass': 1.008, 
                  'oxides': [('H₂O', 18.015), ('H₂O₂', 34.015)], 
                  'nitrates': [('HNO₃', 63.013), ('HNO₃·H₂O', 81.028)]},
            
            'He': {'name': '氦', 'mass': 4.003},
            
            'Li': {'name': '锂', 'mass': 6.941, 
                   'oxides': [('Li₂O', 29.881), ('Li₂O₂', 45.881)], 
                   'nitrates': [('LiNO₃', 68.946), ('LiNO₃·3H₂O', 123.013)]},
            
            'Be': {'name': '铍', 'mass': 9.012, 
                   'oxides': [('BeO', 25.012)], 
                   'nitrates': [('Be(NO₃)₂', 133.022), ('Be(NO₃)₂·4H₂O', 205.083)]},
            
            'B': {'name': '硼', 'mass': 10.811, 
                  'oxides': [('B₂O₃', 69.620), ('B₂O₂', 53.622)], 
                  'nitrates': [('B(NO₃)₃', 196.836), ('B(NO₃)₃·6H₂O', 286.941)]},
            
            'C': {'name': '碳', 'mass': 12.011, 
                  'oxides': [('CO', 28.010), ('CO₂', 44.010), ('C₂O₃', 72.021)], 
                  'nitrates': []},
            
            'N': {'name': '氮', 'mass': 14.007, 
                  'oxides': [('NO', 30.006), ('NO₂', 46.006), ('N₂O', 44.013), ('N₂O₃', 76.012), ('N₂O₄', 92.011), ('N₂O₅', 108.010)], 
                  'nitrates': []},
            
            'O': {'name': '氧', 'mass': 16.000},
            
            'F': {'name': '氟', 'mass': 19.000, 
                  'oxides': [('OF₂', 54.000), ('O₂F₂', 70.000)], 
                  'nitrates': [('FNO₃', 81.005)]},
            
            'Ne': {'name': '氖', 'mass': 20.180},
            
            'Na': {'name': '钠', 'mass': 22.990, 
                   'oxides': [('Na₂O', 61.979), ('Na₂O₂', 77.978), ('NaO₂', 54.989)], 
                   'nitrates': [('NaNO₃', 84.995), ('NaNO₃·H₂O', 102.010), ('NaNO₃·2H₂O', 119.025)]},
            
            'Mg': {'name': '镁', 'mass': 24.305, 
                   'oxides': [('MgO', 40.304), ('MgO₂', 56.304)], 
                   'nitrates': [('Mg(NO₃)₂', 148.315), ('Mg(NO₃)₂·2H₂O', 184.346), 
                               ('Mg(NO₃)₂·4H₂O', 220.376), ('Mg(NO₃)₂·6H₂O', 256.406)]},
            
            'Al': {'name': '铝', 'mass': 26.982, 
                   'oxides': [('Al₂O₃', 101.961), ('AlO', 42.981), ('Al₂O', 69.964)], 
                   'nitrates': [('Al(NO₃)₃', 212.996), ('Al(NO₃)₃·6H₂O', 321.088), 
                               ('Al(NO₃)₃·9H₂O', 375.134), ('Al(NO₃)₃·12H₂O', 429.180)]},
            
            'Si': {'name': '硅', 'mass': 28.086, 
                   'oxides': [('SiO₂', 60.084), ('SiO', 44.085), ('Si₂O₃', 104.171)], 
                   'nitrates': [('Si(NO₃)₄', 312.104)]},
            
            'P': {'name': '磷', 'mass': 30.974, 
                  'oxides': [('P₂O₅', 141.944), ('P₂O₃', 109.945), ('P₄O₆', 219.891), ('P₄O₁₀', 283.889)], 
                  'nitrates': [('P(NO₃)₃', 236.985)]},
            
            'S': {'name': '硫', 'mass': 32.066, 
                  'oxides': [('SO₂', 64.066), ('SO₃', 80.066), ('S₂O', 80.132), ('S₂O₃', 112.131)], 
                  'nitrates': [('S(NO₃)₂', 156.138)]},
            
            'Cl': {'name': '氯', 'mass': 35.453, 
                   'oxides': [('Cl₂O', 86.905), ('ClO₂', 67.453), ('Cl₂O₇', 182.902)], 
                   'nitrates': [('ClNO₃', 97.458)]},
            
            'Ar': {'name': '氩', 'mass': 39.948},
            
            'K': {'name': '钾', 'mass': 39.098, 
                  'oxides': [('K₂O', 94.196), ('K₂O₂', 110.196), ('KO₂', 71.098)], 
                  'nitrates': [('KNO₃', 101.103), ('KNO₃·H₂O', 119.118)]},
            
            'Ca': {'name': '钙', 'mass': 40.078, 
                   'oxides': [('CaO', 56.077), ('CaO₂', 72.077)], 
                   'nitrates': [('Ca(NO₃)₂', 164.088), ('Ca(NO₃)₂·2H₂O', 200.119), 
                               ('Ca(NO₃)₂·4H₂O', 236.149), ('Ca(NO₃)₂·6H₂O', 272.179)]},
            
            'Sc': {'name': '钪', 'mass': 44.956, 
                   'oxides': [('Sc₂O₃', 137.910), ('ScO', 60.955)], 
                   'nitrates': [('Sc(NO₃)₃', 230.971), ('Sc(NO₃)₃·4H₂O', 299.052)]},
            
            'Ti': {'name': '钛', 'mass': 47.867, 
                   'oxides': [('TiO₂', 79.866), ('Ti₂O₃', 143.732), ('TiO', 63.867), ('Ti₃O₅', 223.599)], 
                   'nitrates': [('Ti(NO₃)₄', 295.886), ('Ti(NO₃)₄·2H₂O', 331.917)]},
            
            'V': {'name': '钒', 'mass': 50.942, 
                  'oxides': [('V₂O₅', 181.880), ('VO₂', 82.941), ('V₂O₃', 149.881), ('VO', 66.941)], 
                  'nitrates': [('V(NO₃)₃', 236.955), ('V(NO₃)₃·6H₂O', 325.047)]},
            
            'Cr': {'name': '铬', 'mass': 51.996, 
                   'oxides': [('Cr₂O₃', 151.990), ('CrO₃', 99.994), ('CrO₂', 83.995), ('CrO', 67.996)], 
                   'nitrates': [('Cr(NO₃)₃', 238.011), ('Cr(NO₃)₃·9H₂O', 400.149)]},
            
            'Mn': {'name': '锰', 'mass': 54.938, 
                   'oxides': [('MnO', 70.937), ('MnO₂', 86.937), ('Mn₂O₃', 157.874), ('Mn₃O₄', 228.812)], 
                   'nitrates': [('Mn(NO₃)₂', 178.948), ('Mn(NO₃)₂·4H₂O', 251.009), ('Mn(NO₃)₂·6H₂O', 287.039)]},
            
            'Fe': {'name': '铁', 'mass': 55.845, 
                   'oxides': [('Fe₂O₃', 159.688), ('Fe₃O₄', 231.533), ('FeO', 71.844), ('Fe₂O', 127.689)], 
                   'nitrates': [('Fe(NO₃)₃', 241.860), ('Fe(NO₃)₂', 179.855), ('Fe(NO₃)₃·9H₂O', 404.000)]},
            
            'Co': {'name': '钴', 'mass': 58.933, 
                   'oxides': [('CoO', 74.932), ('Co₃O₄', 240.798), ('Co₂O₃', 165.864)], 
                   'nitrates': [('Co(NO₃)₂', 182.943), ('Co(NO₃)₂·6H₂O', 291.035), ('Co(NO₃)₃', 244.947)]},
            
            'Ni': {'name': '镍', 'mass': 58.693, 
                   'oxides': [('NiO', 74.692), ('Ni₂O₃', 165.385), ('Ni₃O₄', 240.078)], 
                   'nitrates': [('Ni(NO₃)₂', 182.703), ('Ni(NO₃)₂·6H₂O', 290.795), ('Ni(NO₃)₃', 244.707)]},
            
            'Cu': {'name': '铜', 'mass': 63.546, 
                   'oxides': [('CuO', 79.545), ('Cu₂O', 143.091), ('CuO₂', 95.545)], 
                   'nitrates': [('Cu(NO₃)₂', 187.556), ('Cu(NO₃)₂·3H₂O', 241.602), ('Cu(NO₃)₂·6H₂O', 295.647)]},
            
            'Zn': {'name': '锌', 'mass': 65.38, 
                   'oxides': [('ZnO', 81.379), ('ZnO₂', 97.379)], 
                   'nitrates': [('Zn(NO₃)₂', 189.390), ('Zn(NO₃)₂·4H₂O', 255.421), ('Zn(NO₃)₂·6H₂O', 297.441)]},
            
            'Ga': {'name': '镓', 'mass': 69.723, 
                   'oxides': [('Ga₂O₃', 187.444), ('GaO', 85.722)], 
                   'nitrates': [('Ga(NO₃)₃', 255.737), ('Ga(NO₃)₃·8H₂O', 399.873)]},
            
            'Ge': {'name': '锗', 'mass': 72.64, 
                   'oxides': [('GeO₂', 104.639), ('GeO', 88.639)], 
                   'nitrates': [('Ge(NO₃)₄', 348.680)]},
            
            'As': {'name': '砷', 'mass': 74.922, 
                   'oxides': [('As₂O₃', 197.841), ('As₂O₅', 229.840)], 
                   'nitrates': [('As(NO₃)₃', 260.948)]},
            
            'Se': {'name': '硒', 'mass': 78.96, 
                   'oxides': [('SeO₂', 110.959), ('SeO₃', 126.959)], 
                   'nitrates': [('Se(NO₃)₄', 348.960)]},
            
            'Br': {'name': '溴', 'mass': 79.904, 
                   'oxides': [('Br₂O', 175.808), ('BrO₂', 111.904)], 
                   'nitrates': [('BrNO₃', 141.909)]},
            
            'Kr': {'name': '氪', 'mass': 83.80},
            
            'Rb': {'name': '铷', 'mass': 85.468, 
                   'oxides': [('Rb₂O', 186.936), ('RbO₂', 117.468)], 
                   'nitrates': [('RbNO₃', 147.473)]},
            
            'Sr': {'name': '锶', 'mass': 87.62, 
                   'oxides': [('SrO', 103.619), ('SrO₂', 119.619)], 
                   'nitrates': [('Sr(NO₃)₂', 211.630), ('Sr(NO₃)₂·4H₂O', 283.691)]},
            
            'Y': {'name': '钇', 'mass': 88.906, 
                  'oxides': [('Y₂O₃', 225.810), ('YO', 104.905)], 
                  'nitrates': [('Y(NO₃)₃', 274.921), ('Y(NO₃)₃·6H₂O', 383.013)]},
            
            'Zr': {'name': '锆', 'mass': 91.224, 
                   'oxides': [('ZrO₂', 123.223), ('Zr₂O₃', 229.446)], 
                   'nitrates': [('Zr(NO₃)₄', 339.256), ('Zr(NO₃)₄·5H₂O', 429.337)]},
            
            'Nb': {'name': '铌', 'mass': 92.906, 
                   'oxides': [('Nb₂O₅', 265.810), ('NbO₂', 124.905), ('NbO', 108.906)], 
                   'nitrates': [('Nb(NO₃)₅', 438.920)]},
            
            'Mo': {'name': '钼', 'mass': 95.96, 
                   'oxides': [('MoO₃', 143.958), ('MoO₂', 127.959), ('Mo₂O₃', 239.918)], 
                   'nitrates': [('Mo(NO₃)₆', 467.960)]},
            
            'Tc': {'name': '锝', 'mass': 98.0, 
                   'oxides': [('Tc₂O₇', 317.998), ('TcO₂', 130.000)], 
                   'nitrates': [('Tc(NO₃)₄', 321.010)]},
            
            'Ru': {'name': '钌', 'mass': 101.07, 
                   'oxides': [('RuO₂', 133.069), ('RuO₄', 165.068)], 
                   'nitrates': [('Ru(NO₃)₃', 270.085)]},
            
            'Rh': {'name': '铑', 'mass': 102.906, 
                   'oxides': [('Rh₂O₃', 253.809), ('RhO₂', 134.905)], 
                   'nitrates': [('Rh(NO₃)₃', 271.921)]},
            
            'Pd': {'name': '钯', 'mass': 106.42, 
                   'oxides': [('PdO', 122.419), ('PdO₂', 138.419)], 
                   'nitrates': [('Pd(NO₃)₂', 230.430)]},
            
            'Ag': {'name': '银', 'mass': 107.868, 
                   'oxides': [('Ag₂O', 231.735), ('AgO', 123.868)], 
                   'nitrates': [('AgNO₃', 169.873), ('AgNO₃·H₂O', 187.888)]},
            
            'Cd': {'name': '镉', 'mass': 112.411, 
                   'oxides': [('CdO', 128.410), ('CdO₂', 144.410)], 
                   'nitrates': [('Cd(NO₃)₂', 236.421), ('Cd(NO₃)₂·4H₂O', 308.482)]},
            
            'In': {'name': '铟', 'mass': 114.818, 
                   'oxides': [('In₂O₃', 277.634), ('InO', 130.817)], 
                   'nitrates': [('In(NO₃)₃', 300.832), ('In(NO₃)₃·5H₂O', 390.913)]},
            
            'Sn': {'name': '锡', 'mass': 118.710, 
                   'oxides': [('SnO₂', 150.709), ('SnO', 134.709)], 
                   'nitrates': [('Sn(NO₃)₄', 366.730), ('Sn(NO₃)₄·4H₂O', 438.791)]},
            
            'Sb': {'name': '锑', 'mass': 121.760, 
                   'oxides': [('Sb₂O₃', 291.518), ('Sb₂O₅', 323.517), ('SbO₂', 153.759)], 
                   'nitrates': [('Sb(NO₃)₃', 282.785)]},
            
            'Te': {'name': '碲', 'mass': 127.60, 
                   'oxides': [('TeO₂', 159.599), ('TeO₃', 175.599)], 
                   'nitrates': [('Te(NO₃)₄', 400.620)]},
            
            'I': {'name': '碘', 'mass': 126.904, 
                  'oxides': [('I₂O₅', 333.806), ('I₂O₄', 317.807)], 
                  'nitrates': [('INO₃', 172.909)]},
            
            'Xe': {'name': '氙', 'mass': 131.29},
            
            'Cs': {'name': '铯', 'mass': 132.905, 
                   'oxides': [('Cs₂O', 281.810), ('CsO₂', 164.905)], 
                   'nitrates': [('CsNO₃', 194.910)]},
            
            'Ba': {'name': '钡', 'mass': 137.327, 
                   'oxides': [('BaO', 153.326), ('BaO₂', 169.326)], 
                   'nitrates': [('Ba(NO₃)₂', 261.337), ('Ba(NO₃)₂·4H₂O', 333.398)]},
            
            'La': {'name': '镧', 'mass': 138.905, 
                   'oxides': [('La₂O₃', 325.808), ('LaO', 154.904)], 
                   'nitrates': [('La(NO₃)₃', 324.920), ('La(NO₃)₃·6H₂O', 433.012)]},
            
            'Ce': {'name': '铈', 'mass': 140.116, 
                   'oxides': [('CeO₂', 172.115), ('Ce₂O₃', 328.230)], 
                   'nitrates': [('Ce(NO₃)₃', 326.131), ('Ce(NO₃)₄', 388.256)]},
            
            'Pr': {'name': '镨', 'mass': 140.908, 
                   'oxides': [('Pr₂O₃', 329.813), ('PrO₂', 172.907)], 
                   'nitrates': [('Pr(NO₃)₃', 326.923), ('Pr(NO₃)₃·6H₂O', 435.015)]},
            
            'Nd': {'name': '钕', 'mass': 144.242, 
                   'oxides': [('Nd₂O₃', 336.482), ('NdO', 160.241)], 
                   'nitrates': [('Nd(NO₃)₃', 330.257), ('Nd(NO₃)₃·6H₂O', 438.349)]},
            
            'Pm': {'name': '钷', 'mass': 145.0, 
                   'oxides': [('Pm₂O₃', 338.0)], 
                   'nitrates': [('Pm(NO₃)₃', 332.015)]},
            
            'Sm': {'name': '钐', 'mass': 150.36, 
                   'oxides': [('Sm₂O₃', 348.718), ('SmO', 166.359)], 
                   'nitrates': [('Sm(NO₃)₃', 336.375), ('Sm(NO₃)₃·6H₂O', 444.467)]},
            
            'Eu': {'name': '铕', 'mass': 151.964, 
                   'oxides': [('Eu₂O₃', 351.926), ('EuO', 167.963)], 
                   'nitrates': [('Eu(NO₃)₃', 337.979), ('Eu(NO₃)₃·6H₂O', 446.071)]},
            
            'Gd': {'name': '钆', 'mass': 157.25, 
                   'oxides': [('Gd₂O₃', 362.498), ('GdO', 173.249)], 
                   'nitrates': [('Gd(NO₃)₃', 343.265), ('Gd(NO₃)₃·6H₂O', 451.357)]},
            
            'Tb': {'name': '铽', 'mass': 158.925, 
                   'oxides': [('Tb₂O₃', 365.848), ('TbO₂', 190.924)], 
                   'nitrates': [('Tb(NO₃)₃', 344.940), ('Tb(NO₃)₃·6H₂O', 453.032)]},
            
            'Dy': {'name': '镝', 'mass': 162.500, 
                   'oxides': [('Dy₂O₃', 372.998), ('DyO', 178.499)], 
                   'nitrates': [('Dy(NO₃)₃', 348.515), ('Dy(NO₃)₃·6H₂O', 456.607)]},
            
            'Ho': {'name': '钬', 'mass': 164.930, 
                   'oxides': [('Ho₂O₃', 377.858), ('HoO', 180.929)], 
                   'nitrates': [('Ho(NO₃)₃', 350.945), ('Ho(NO₃)₃·6H₂O', 459.037)]},
            
            'Er': {'name': '铒', 'mass': 167.259, 
                   'oxides': [('Er₂O₃', 382.516), ('ErO', 183.258)], 
                   'nitrates': [('Er(NO₃)₃', 353.274), ('Er(NO₃)₃·6H₂O', 461.366)]},
            
            'Tm': {'name': '铥', 'mass': 168.934, 
                   'oxides': [('Tm₂O₃', 385.866), ('TmO', 184.933)], 
                   'nitrates': [('Tm(NO₃)₃', 354.949), ('Tm(NO₃)₃·6H₂O', 463.041)]},
            
            'Yb': {'name': '镱', 'mass': 173.054, 
                   'oxides': [('Yb₂O₃', 394.106), ('YbO', 189.053)], 
                   'nitrates': [('Yb(NO₃)₃', 359.069), ('Yb(NO₃)₃·6H₂O', 467.161)]},
            
            'Lu': {'name': '镥', 'mass': 174.967, 
                   'oxides': [('Lu₂O₃', 397.932), ('LuO', 190.966)], 
                   'nitrates': [('Lu(NO₃)₃', 360.982), ('Lu(NO₃)₃·6H₂O', 469.074)]},
            
            'Hf': {'name': '铪', 'mass': 178.49, 
                   'oxides': [('HfO₂', 210.489), ('Hf₂O₃', 394.978)], 
                   'nitrates': [('Hf(NO₃)₄', 426.522), ('Hf(NO₃)₄·5H₂O', 516.603)]},
            
            'Ta': {'name': '钽', 'mass': 180.948, 
                   'oxides': [('Ta₂O₅', 441.893), ('TaO₂', 212.947)], 
                   'nitrates': [('Ta(NO₃)₅', 488.962)]},
            
            'W': {'name': '钨', 'mass': 183.84, 
                  'oxides': [('WO₃', 231.839), ('WO₂', 215.839), ('W₂O₅', 447.677)], 
                  'nitrates': [('W(NO₃)₆', 515.840)]},
            
            'Re': {'name': '铼', 'mass': 186.207, 
                   'oxides': [('Re₂O₇', 484.411), ('ReO₃', 234.206), ('ReO₂', 218.206)], 
                   'nitrates': [('Re(NO₃)₅', 498.222)]},
            
            'Os': {'name': '锇', 'mass': 190.23, 
                   'oxides': [('OsO₄', 254.229), ('OsO₂', 222.229)], 
                   'nitrates': [('Os(NO₃)₄', 411.250)]},
            
            'Ir': {'name': '铱', 'mass': 192.217, 
                   'oxides': [('IrO₂', 224.216), ('Ir₂O₃', 432.431)], 
                   'nitrates': [('Ir(NO₃)₃', 331.232)]},
            
            'Pt': {'name': '铂', 'mass': 195.084, 
                   'oxides': [('PtO₂', 227.083), ('PtO', 211.083)], 
                   'nitrates': [('Pt(NO₃)₂', 319.089), ('Pt(NO₃)₄', 409.184)]},
            
            'Au': {'name': '金', 'mass': 196.967, 
                   'oxides': [('Au₂O₃', 441.931), ('AuO', 212.966)], 
                   'nitrates': [('Au(NO₃)₃', 382.982)]},
            
            'Hg': {'name': '汞', 'mass': 200.59, 
                   'oxides': [('HgO', 216.589), ('Hg₂O', 433.178)], 
                   'nitrates': [('Hg(NO₃)₂', 324.600), ('Hg(NO₃)₂·H₂O', 342.615)]},
            
            'Tl': {'name': '铊', 'mass': 204.38, 
                   'oxides': [('Tl₂O₃', 456.758), ('Tl₂O', 424.759)], 
                   'nitrates': [('TlNO₃', 266.385), ('Tl(NO₃)₃', 390.395)]},
            
            'Pb': {'name': '铅', 'mass': 207.2, 
                   'oxides': [('PbO', 223.199), ('PbO₂', 239.199), ('Pb₃O₄', 685.598)], 
                   'nitrates': [('Pb(NO₃)₂', 331.210), ('Pb(NO₃)₄', 455.220)]},
            
            'Bi': {'name': '铋', 'mass': 208.980, 
                   'oxides': [('Bi₂O₃', 465.959), ('BiO', 224.979)], 
                   'nitrates': [('Bi(NO₃)₃', 394.995), ('Bi(NO₃)₃·5H₂O', 485.076)]},
            
            'Po': {'name': '钋', 'mass': 209.0, 
                   'oxides': [('PoO₂', 241.0)], 
                   'nitrates': [('Po(NO₃)₄', 421.020)]},
            
            'At': {'name': '砹', 'mass': 210.0, 
                   'oxides': [('At₂O', 422.0)], 
                   'nitrates': [('AtNO₃', 255.005)]},
            
            'Rn': {'name': '氡', 'mass': 222.0},
            
            'Fr': {'name': '钫', 'mass': 223.0, 
                   'oxides': [('Fr₂O', 446.0)], 
                   'nitrates': [('FrNO₃', 268.005)]},
            
            'Ra': {'name': '镭', 'mass': 226.0, 
                   'oxides': [('RaO', 242.0)], 
                   'nitrates': [('Ra(NO₃)₂', 350.010)]},
            
            'Ac': {'name': '锕', 'mass': 227.0, 
                   'oxides': [('Ac₂O₃', 502.0)], 
                   'nitrates': [('Ac(NO₃)₃', 393.015)]},
            
            'Th': {'name': '钍', 'mass': 232.038, 
                   'oxides': [('ThO₂', 264.037)], 
                   'nitrates': [('Th(NO₃)₄', 480.172), ('Th(NO₃)₄·4H₂O', 552.233)]},
            
            'Pa': {'name': '镤', 'mass': 231.036, 
                   'oxides': [('Pa₂O₅', 542.069)], 
                   'nitrates': [('Pa(NO₃)₅', 541.050)]},
            
            'U': {'name': '铀', 'mass': 238.029, 
                  'oxides': [('UO₂', 270.028), ('UO₃', 286.028), ('U₃O₈', 842.085)], 
                  'nitrates': [('U(NO₃)₄', 502.185), ('UO₂(NO₃)₂', 394.037)]},
        }
        
        # 自定义化合物存储文件
        self.custom_file = "custom_compounds.json"
        self.load_custom_compounds()
    
    def load_custom_compounds(self):
        """加载自定义化合物"""
        if os.path.exists(self.custom_file):
            try:
                with open(self.custom_file, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                    for element_symbol, compounds in custom_data.items():
                        if element_symbol in self.elements:
                            # 添加自定义化合物
                            if 'nitrates' in compounds:
                                if 'nitrates' not in self.elements[element_symbol]:
                                    self.elements[element_symbol]['nitrates'] = []
                                # 避免重复添加
                                existing_nitrates = {n[0] for n in self.elements[element_symbol]['nitrates']}
                                for nitrate in compounds['nitrates']:
                                    if nitrate[0] not in existing_nitrates:
                                        self.elements[element_symbol]['nitrates'].append(nitrate)
            except Exception as e:
                print(f"加载自定义化合物失败: {e}")
    
    def save_custom_compounds(self):
        """保存自定义化合物"""
        try:
            custom_data = {}
            for element_symbol, info in self.elements.items():
                custom_nitrates = []
                # 只保存自定义的硝酸盐（如果有标记的话）
                # 这里简化处理：保存所有硝酸盐
                if 'nitrates' in info:
                    custom_nitrates = info['nitrates']
                
                if custom_nitrates:
                    custom_data[element_symbol] = {'nitrates': custom_nitrates}
            
            with open(self.custom_file, 'w', encoding='utf-8') as f:
                json.dump(custom_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义化合物失败: {e}")
    
    def add_custom_nitrate(self, element_symbol, nitrate_formula, nitrate_mass):
        """添加自定义硝酸盐"""
        element_symbol = element_symbol.strip().title()
        if element_symbol not in self.elements:
            # 如果元素不存在，先添加基本元素信息
            self.elements[element_symbol] = {
                'name': element_symbol,
                'mass': 0.0,
                'oxides': [],
                'nitrates': []
            }
        
        if 'nitrates' not in self.elements[element_symbol]:
            self.elements[element_symbol]['nitrates'] = []
        
        # 避免重复添加
        for nitrate, _ in self.elements[element_symbol]['nitrates']:
            if nitrate == nitrate_formula:
                return False
        
        self.elements[element_symbol]['nitrates'].append((nitrate_formula, nitrate_mass))
        self.save_custom_compounds()
        return True
    
    def get_element_info(self, symbol):
        """获取元素信息"""
        symbol = symbol.strip().title()
        if symbol in self.elements:
            return self.elements[symbol]
        return None

class PlaceholderEntry(tk.Entry):
    """带占位符的输入框"""
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_fg_color = self["fg"]
        
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
        self.put_placeholder()
    
    def put_placeholder(self):
        """显示占位符"""
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)
    
    def on_focus_in(self, event):
        """获得焦点时清除占位符"""
        if self["fg"] == self.placeholder_color:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg_color)
    
    def on_focus_out(self, event):
        """失去焦点时显示占位符（如果为空）"""
        if not self.get():
            self.put_placeholder()

class PeriodicTableWindow:
    """元素周期表窗口"""
    def __init__(self, parent, element_info, callback=None):
        self.parent = parent
        self.element_info = element_info
        self.callback = callback  # 回调函数，用于插入分子量
        
        self.window = tk.Toplevel(parent)
        self.window.title("元素周期表")
        self.window.geometry("1000x700")
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 主族元素标签页
        main_group_frame = ttk.Frame(notebook)
        notebook.add(main_group_frame, text="主族元素")
        self.create_main_periodic_table(main_group_frame)
        
        # 镧系元素标签页
        lanthanide_frame = ttk.Frame(notebook)
        notebook.add(lanthanide_frame, text="镧系元素")
        self.create_lanthanide_table(lanthanide_frame)
        
        # 锕系元素标签页
        actinide_frame = ttk.Frame(notebook)
        notebook.add(actinide_frame, text="锕系元素")
        self.create_actinide_table(actinide_frame)
        
        # 信息显示区域
        info_frame = ttk.LabelFrame(main_frame, text="元素信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # 元素详细信息
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="插入到Mx", 
                  command=lambda: self.insert_to_input('mx')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="插入到Mz", 
                  command=lambda: self.insert_to_input('mz')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="添加自定义化合物", 
                  command=self.show_add_custom_dialog).pack(side=tk.LEFT, padx=5)
        
        # 当前选中的元素
        self.current_element = None
        self.current_mass = None
    
    def create_main_periodic_table(self, parent):
        """创建主族元素周期表 - 使用网格严格对齐"""
        # 使用网格布局
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, pady=10)
        
        # 定义元素位置 - 标准的周期表布局 (族: 1-18, 周期: 1-7)
        # 每个元素用 (周期, 族, 元素符号) 表示
        element_positions = [
            # 周期 1
            (1, 1, "H"), (1, 18, "He"),
            
            # 周期 2
            (2, 1, "Li"), (2, 2, "Be"),
            (2, 13, "B"), (2, 14, "C"), (2, 15, "N"), (2, 16, "O"), (2, 17, "F"), (2, 18, "Ne"),
            
            # 周期 3
            (3, 1, "Na"), (3, 2, "Mg"),
            (3, 13, "Al"), (3, 14, "Si"), (3, 15, "P"), (3, 16, "S"), (3, 17, "Cl"), (3, 18, "Ar"),
            
            # 周期 4
            (4, 1, "K"), (4, 2, "Ca"),
            (4, 3, "Sc"), (4, 4, "Ti"), (4, 5, "V"), (4, 6, "Cr"), (4, 7, "Mn"), (4, 8, "Fe"), 
            (4, 9, "Co"), (4, 10, "Ni"), (4, 11, "Cu"), (4, 12, "Zn"),
            (4, 13, "Ga"), (4, 14, "Ge"), (4, 15, "As"), (4, 16, "Se"), (4, 17, "Br"), (4, 18, "Kr"),
            
            # 周期 5
            (5, 1, "Rb"), (5, 2, "Sr"),
            (5, 3, "Y"), (5, 4, "Zr"), (5, 5, "Nb"), (5, 6, "Mo"), (5, 7, "Tc"), (5, 8, "Ru"), 
            (5, 9, "Rh"), (5, 10, "Pd"), (5, 11, "Ag"), (5, 12, "Cd"),
            (5, 13, "In"), (5, 14, "Sn"), (5, 15, "Sb"), (5, 16, "Te"), (5, 17, "I"), (5, 18, "Xe"),
            
            # 周期 6
            (6, 1, "Cs"), (6, 2, "Ba"),
            (6, 3, "La"),
            (6, 4, "Hf"), (6, 5, "Ta"), (6, 6, "W"), (6, 7, "Re"), (6, 8, "Os"), 
            (6, 9, "Ir"), (6, 10, "Pt"), (6, 11, "Au"), (6, 12, "Hg"),
            (6, 13, "Tl"), (6, 14, "Pb"), (6, 15, "Bi"), (6, 16, "Po"), (6, 17, "At"), (6, 18, "Rn"),
            
            # 周期 7
            (7, 1, "Fr"), (7, 2, "Ra"),
            (7, 3, "Ac"),
            (7, 4, "Rf"), (7, 5, "Db"), (7, 6, "Sg"), (7, 7, "Bh"), (7, 8, "Hs"), 
            (7, 9, "Mt"), (7, 10, "Ds"), (7, 11, "Rg"), (7, 12, "Cn"),
            (7, 13, "Nh"), (7, 14, "Fl"), (7, 15, "Mc"), (7, 16, "Lv"), (7, 17, "Ts"), (7, 18, "Og"),
        ]
        
        # 传统元素周期表族标题 (1-18族)
        # 使用罗马数字和A/B标记
        group_labels = {
            1: "IA",  2: "IIA",  3: "IIIB",  4: "IVB",  5: "VB",   6: "VIB",
            7: "VIIB", 8: "VIII", 9: "VIII", 10: "VIII", 11: "IB",  12: "IIB",
            13: "IIIA", 14: "IVA", 15: "VA",  16: "VIA", 17: "VIIA", 18: "0"
        }
        
        # 族标题 (1-18)
        for group in range(1, 19):
            label = ttk.Label(table_frame, text=group_labels.get(group, str(group)), 
                            width=4, anchor="center", font=("Arial", 8, "bold"))
            label.grid(row=0, column=group, padx=1, pady=(0, 5))
        
        # 放置元素
        for period, group, element in element_positions:
            if element:
                btn = ttk.Button(table_frame, text=element, width=4,
                               command=lambda e=element: self.show_element_info(e))
                btn.grid(row=period, column=group, padx=1, pady=1, sticky="nsew")
        
        # 设置网格权重，让所有单元格均匀分布
        for i in range(1, 8):  # 1-7周期
            table_frame.grid_rowconfigure(i, weight=1, uniform="row")
        
        for j in range(1, 19):  # 1-18族
            table_frame.grid_columnconfigure(j, weight=1, uniform="col")
        
        # 添加镧系和锕系占位符说明
        note_frame = ttk.Frame(parent)
        note_frame.pack(pady=5)
        
        ttk.Label(note_frame, text="注：镧系和锕系元素请查看对应标签页", 
                 font=("Arial", 9, "italic")).pack()
    
    def create_lanthanide_table(self, parent):
        """创建镧系元素表"""
        lanthanides = [
            "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", 
            "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"
        ]
        
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, pady=20)
        
        ttk.Label(table_frame, text="镧系元素:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=15, pady=5)
        
        # 放置镧系元素
        for i, element in enumerate(lanthanides):
            btn = ttk.Button(table_frame, text=element, width=4,
                           command=lambda e=element: self.show_element_info(e))
            btn.grid(row=1, column=i, padx=2, pady=2)
        
        # 设置网格均匀分布
        for i in range(15):
            table_frame.grid_columnconfigure(i, weight=1)
    
    def create_actinide_table(self, parent):
        """创建锕系元素表"""
        actinides = [
            "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", 
            "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"
        ]
        
        table_frame = ttk.Frame(parent)
        table_frame.pack(expand=True, pady=20)
        
        ttk.Label(table_frame, text="锕系元素:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=15, pady=5)
        
        # 放置锕系元素
        for i, element in enumerate(actinides):
            btn = ttk.Button(table_frame, text=element, width=4,
                           command=lambda e=element: self.show_element_info(e))
            btn.grid(row=1, column=i, padx=2, pady=2)
        
        # 设置网格均匀分布
        for i in range(15):
            table_frame.grid_columnconfigure(i, weight=1)
    
    def show_element_info(self, element_symbol):
        """显示元素信息"""
        info = self.element_info.get_element_info(element_symbol)
        if info:
            self.current_element = element_symbol
            self.current_mass = info['mass']
            
            text = f"元素: {element_symbol} ({info['name']})\n"
            text += f"原子量: {info['mass']:.3f}\n\n"
            
            if 'oxides' in info and info['oxides']:
                text += "常见氧化物:\n"
                for oxide, mass in info['oxides']:
                    text += f"  {oxide}: {mass:.3f}\n"
            
            if 'nitrates' in info and info['nitrates']:
                text += "\n常见硝酸盐:\n"
                for nitrate, mass in info['nitrates']:
                    # 区分含水和无水
                    if 'H₂O' in nitrate:
                        text += f"  {nitrate} (含水): {mass:.3f}\n"
                    else:
                        text += f"  {nitrate} (无水): {mass:.3f}\n"
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, text)
        else:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"元素 {element_symbol} 的信息暂未收录")
    
    def insert_to_input(self, target):
        """插入到输入框"""
        if self.current_element and self.current_mass and self.callback:
            self.callback(target, self.current_mass)
            self.window.destroy()
    
    def show_add_custom_dialog(self):
        """显示添加自定义化合物对话框"""
        if not self.current_element:
            messagebox.showwarning("提示", "请先选择一个元素")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title(f"为 {self.current_element} 添加自定义化合物")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"为元素 {self.current_element} 添加化合物", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 15))
        
        # 硝酸盐化学式
        ttk.Label(main_frame, text="化合物化学式:").pack(anchor=tk.W, pady=5)
        formula_entry = ttk.Entry(main_frame, width=30)
        formula_entry.pack(pady=5)
        formula_entry.insert(0, f"{self.current_element}(NO₃)ₓ")
        
        # 相对分子质量
        ttk.Label(main_frame, text="相对分子质量:").pack(anchor=tk.W, pady=5)
        mass_entry = ttk.Entry(main_frame, width=30)
        mass_entry.pack(pady=5)
        mass_entry.insert(0, "0.000")
        
        # 示例标签
        example_frame = ttk.LabelFrame(main_frame, text="示例", padding=10)
        example_frame.pack(fill=tk.X, pady=10)
        
        examples = [
            "AgNO₃·H₂O (硝酸银一水合物)",
            "Cu(NO₃)₂·3H₂O (硝酸铜三水合物)",
            "Al(NO₃)₃·9H₂O (硝酸铝九水合物)"
        ]
        
        for example in examples:
            ttk.Label(example_frame, text=example, font=("Arial", 9)).pack(anchor=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        def add_compound():
            formula = formula_entry.get().strip()
            mass_str = mass_entry.get().strip()
            
            if not formula:
                messagebox.showerror("错误", "请输入化合物化学式")
                return
            
            try:
                mass = float(mass_str)
                if mass <= 0:
                    messagebox.showerror("错误", "相对分子质量必须大于0")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
                return
            
            # 添加自定义化合物
            if self.element_info.add_custom_nitrate(self.current_element, formula, mass):
                messagebox.showinfo("成功", f"已为 {self.current_element} 添加化合物: {formula}")
                # 刷新显示
                self.show_element_info(self.current_element)
                dialog.destroy()
            else:
                messagebox.showwarning("提示", "该化合物已存在")
        
        def import_from_file():
            """从文件导入化合物"""
            filename = filedialog.askopenfilename(
                title="选择化合物数据文件",
                filetypes=[("CSV文件", "*.csv"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    added_count = 0
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split(',')
                            if len(parts) >= 3:
                                element = parts[0].strip().title()
                                formula = parts[1].strip()
                                try:
                                    mass = float(parts[2].strip())
                                    if self.element_info.add_custom_nitrate(element, formula, mass):
                                        added_count += 1
                                except ValueError:
                                    continue
                    
                    messagebox.showinfo("导入完成", f"成功导入 {added_count} 个化合物")
                    if self.current_element:
                        self.show_element_info(self.current_element)
                    
                except Exception as e:
                    messagebox.showerror("导入失败", f"导入文件时出错: {str(e)}")
        
        ttk.Button(button_frame, text="添加", command=add_compound, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="从文件导入", command=import_from_file, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)

class CatalystCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("负载型催化剂计算器        by-lhw")
        self.root.geometry("900x650")
        
        # 初始化管理器
        self.history_manager = HistoryManager()
        self.element_info = ElementInfo()
        
        # 设置样式
        self.setup_styles()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 配置网格权重
        self.setup_grid_weights()
        
        # 创建界面
        self.create_input_section()
        self.create_result_section()
        self.create_history_section()
        self.create_buttons()
        
        # 绑定事件
        self.root.bind('<Return>', lambda e: self.calculate())
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat")
        style.configure("Title.TLabel", font=("微软雅黑", 12, "bold"))
        style.configure("Result.TLabel", font=("微软雅黑", 10, "bold"))
        style.configure("History.TFrame", relief="solid", borderwidth=1)
    
    def setup_grid_weights(self):
        """配置网格权重"""
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=2)
    
    def create_input_section(self):
        """创建输入区域"""
        # 输入框架
        input_frame = ttk.LabelFrame(self.main_frame, text="输入参数", padding=15)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 输入字段配置
        fields = [
            ("负载量 (wt.%):", "loading", "输入负载量，如: 5.0"),
            ("载体质量 (g):", "support", "输入载体质量，如: 1.000"),
            ("活性组分分子量 (Mx):", "mx", "输入活性组分分子量"),
            ("前驱体分子量 (Mz):", "mz", "输入前驱体分子量"),
        ]
        
        self.entries = {}
        for i, (label, key, placeholder) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=5, pady=8, sticky="e")
            
            # 创建带占位符的输入框
            entry = PlaceholderEntry(input_frame, width=30, placeholder=placeholder)
            entry.grid(row=i, column=1, padx=5, pady=8, sticky="w")
            
            self.entries[key] = entry
        
        # 添加元素周期表按钮
        ttk.Button(input_frame, text="打开元素周期表", 
                  command=self.show_periodic_table, width=20).grid(row=4, column=0, columnspan=2, pady=15)
    
    def create_result_section(self):
        """创建结果显示区域"""
        # 结果框架
        result_frame = ttk.LabelFrame(self.main_frame, text="计算结果", padding=15)
        result_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # 结果字段
        results = [
            ("f (质量分数):", "f"),
            ("mx (活性组分质量):", "mx"),
            ("成品总质量:", "total_finished"),
            ("制后总质量:", "total_after"),
        ]
        
        self.result_labels = {}
        for i, (label, key) in enumerate(results):
            ttk.Label(result_frame, text=label).grid(row=i, column=0, padx=5, pady=8, sticky="e")
            result_label = ttk.Label(result_frame, text="--", style="Result.TLabel", foreground="blue")
            result_label.grid(row=i, column=1, padx=5, pady=8, sticky="w")
            self.result_labels[key] = result_label
        
        # 前驱体质量（重点显示）
        ttk.Label(result_frame, text="所需前驱体质量 (g):", 
                 font=("微软雅黑", 10, "bold")).grid(row=4, column=0, padx=5, pady=8, sticky="e")
        self.precursor_label = ttk.Label(result_frame, text="--", 
                                        font=("微软雅黑", 11, "bold"), foreground="red")
        self.precursor_label.grid(row=4, column=1, padx=5, pady=8, sticky="w")
        
        # 复制按钮
        self.copy_btn = ttk.Button(result_frame, text="复制前驱体质量", 
                                  command=self.copy_precursor_mass, state="disabled")
        self.copy_btn.grid(row=5, column=0, columnspan=2, pady=10)
    
    def create_history_section(self):
        """创建历史记录区域"""
        # 历史记录框架
        history_frame = ttk.LabelFrame(self.main_frame, text="计算历史 (保存到本地，关闭软件不丢失)", padding=10)
        history_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        
        # 创建滚动文本框显示历史
        self.history_text = scrolledtext.ScrolledText(history_frame, height=10)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="清空历史", command=self.clear_history).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="导出到Excel", command=self.export_history).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="刷新历史", command=self.refresh_history).pack(side=tk.RIGHT, padx=5)
        
        # 加载历史记录
        self.refresh_history()
    
    def create_buttons(self):
        """创建按钮区域"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        # 计算按钮
        self.calc_btn = ttk.Button(button_frame, text="开始计算", command=self.calculate, width=15)
        self.calc_btn.pack(side=tk.LEFT, padx=10)
        
        # 重置按钮
        ttk.Button(button_frame, text="重置输入", command=self.reset_inputs, width=15).pack(side=tk.LEFT, padx=10)
        
        # 退出按钮
        ttk.Button(button_frame, text="退出程序", command=self.root.quit, width=15).pack(side=tk.LEFT, padx=10)
    
    def show_periodic_table(self):
        """显示元素周期表窗口"""
        PeriodicTableWindow(self.root, self.element_info, self.insert_mass_to_input)
    
    def insert_mass_to_input(self, target, mass):
        """将分子量插入到输入框"""
        if target in self.entries:
            entry = self.entries[target]
            entry.delete(0, tk.END)
            entry.insert(0, f"{mass:.3f}")
    
    def calculate(self):
        """执行计算"""
        try:
            # 获取输入值
            inputs = {}
            for key, entry in self.entries.items():
                value = entry.get()
                # 如果是占位符，使用默认值0
                if value in ["输入负载量，如: 5.0", "输入载体质量，如: 1.000", 
                           "输入活性组分分子量", "输入前驱体分子量"]:
                    value = "0"
                
                try:
                    inputs[key] = float(value)
                except ValueError:
                    messagebox.showerror("输入错误", f"请输入有效的数字: {key}")
                    return
            
            # 验证输入
            if inputs['loading'] >= 100:
                messagebox.showerror("错误", "负载量不能大于等于100%")
                return
            
            if inputs['loading'] < 0:
                messagebox.showerror("错误", "负载量不能为负数")
                return
            
            if inputs['support'] <= 0:
                messagebox.showerror("错误", "载体质量必须大于0")
                return
            
            if inputs['mx'] <= 0:
                messagebox.showerror("错误", "活性组分分子量必须大于0")
                return
            
            if inputs['mz'] <= 0:
                messagebox.showerror("错误", "前驱体分子量必须大于0")
                return
            
            # 计算
            loading = inputs['loading']
            m_support = inputs['support']
            mx_mol = inputs['mx']
            mz_mol = inputs['mz']
            
            # 1. 计算 f (x在z中的质量分数)
            f = mx_mol / mz_mol if mz_mol != 0 else 0
            
            # 2. 计算成品总质量
            total_finished = m_support / (1 - loading / 100) if loading != 100 else 0
            
            # 3. 计算 mx (活性组分质量)
            mx_mass = total_finished - m_support
            
            # 4. 计算所需前驱体质量
            m_precursor = mx_mass / f if f != 0 else 0
            
            # 5. 制后总质量
            total_after = m_support + m_precursor
            
            # 显示结果
            self.result_labels['f'].config(text=f"{f:.9f}")
            self.result_labels['mx'].config(text=f"{mx_mass:.9f}")
            self.result_labels['total_finished'].config(text=f"{total_finished:.3f}")
            self.result_labels['total_after'].config(text=f"{total_after:.3f}")
            self.precursor_label.config(text=f"{m_precursor:.3f}")
            
            # 启用复制按钮
            self.copy_btn.config(state="normal")
            
            # 保存到历史记录
            results = {
                'f': f"{f:.9f}",
                'mx_mass': f"{mx_mass:.9f}",
                'total_finished': f"{total_finished:.3f}",
                'total_after': f"{total_after:.3f}",
                'precursor_mass': f"{m_precursor:.3f}"
            }
            
            self.history_manager.add_record(inputs, results)
            self.refresh_history()
            
            # 自动复制前驱体质量到剪贴板
            self.copy_precursor_mass()
            
            # 显示成功消息
            self.root.title(f"负载型催化剂计算器 - 计算结果: {m_precursor:.3f}g        by-lhw")
            
        except ZeroDivisionError:
            messagebox.showerror("计算错误", "除数不能为零，请检查输入")
        except Exception as e:
            messagebox.showerror("计算错误", f"发生错误: {str(e)}")
    
    def copy_precursor_mass(self):
        """复制前驱体质量到剪贴板"""
        precursor_mass = self.precursor_label.cget("text")
        if precursor_mass != "--":
            # 使用tkinter内置的剪贴板功能
            self.root.clipboard_clear()
            self.root.clipboard_append(precursor_mass)
            
            # 显示提示
            messagebox.showinfo("复制成功", f"前驱体质量 {precursor_mass}g 已复制到剪贴板")
    
    def refresh_history(self):
        """刷新历史记录显示"""
        history = self.history_manager.get_history()
        self.history_text.delete(1.0, tk.END)
        
        if not history:
            self.history_text.insert(1.0, "暂无历史记录")
            return
        
        for record in reversed(history):  # 最新的在最前面
            text = f"时间: {record['timestamp']}\n"
            text += f"输入: 负载量={record['inputs'].get('loading', 0)}wt.%, "
            text += f"载体={record['inputs'].get('support', 0)}g, "
            text += f"Mx={record['inputs'].get('mx', 0)}, "
            text += f"Mz={record['inputs'].get('mz', 0)}\n"
            text += f"结果: 前驱体质量={record['results'].get('precursor_mass', 0)}g\n"
            text += "-" * 60 + "\n"
            
            self.history_text.insert(1.0, text)
    
    def clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.history_manager.history = []
            self.history_manager.save_history()
            self.refresh_history()
    
    def export_history(self):
        """导出历史记录到Excel"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Excel文件", "*.csv"), ("所有文件", "*.*")],
            title="保存历史记录"
        )
        
        if filename:
            if self.history_manager.export_to_excel(filename):
                messagebox.showinfo("导出成功", f"历史记录已导出到:\n{filename}")
            else:
                messagebox.showerror("导出失败", "导出历史记录失败，请重试")
    
    def reset_inputs(self):
        """重置所有输入框"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            # 重新显示占位符
            if hasattr(entry, 'put_placeholder'):
                entry.put_placeholder()
        
        # 重置结果显示
        for label in self.result_labels.values():
            label.config(text="--")
        self.precursor_label.config(text="--")
        self.copy_btn.config(state="disabled")
        
        self.root.title("负载型催化剂计算器        by-lhw")

def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置窗口图标和标题
    root.title("负载型催化剂计算器        by-lhw")
    
    # 创建应用程序
    app = CatalystCalculator(root)
    
    # 设置窗口最小大小
    root.minsize(900, 650)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()