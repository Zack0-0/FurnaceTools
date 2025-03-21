# 作者：Zack
# 日期：2025/3/13

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CoolingPredictorApp:
    def __init__(self, master):
        self.master = master
        master.title("温度冷却预测器")

        style = ttk.Style()
        style.configure('.', font=('微软雅黑', 10))
        

        # 输入组件
        self.frame_input = ttk.Frame(master)
        self.frame_input.pack(padx=10, pady=10, fill=tk.X)

        # 环境温度
        ttk.Label(self.frame_input, text="环境温度 (℃):").grid(row=0, column=0, sticky=tk.W)
        self.entry_env_temp = ttk.Entry(self.frame_input)
        self.entry_env_temp.insert(0, "20")
        self.entry_env_temp.grid(row=0, column=1, sticky=tk.W)

        # 目标温度
        ttk.Label(self.frame_input, text="目标温度 (℃):").grid(row=1, column=0, sticky=tk.W)
        self.entry_target_temp = ttk.Entry(self.frame_input)
        self.entry_target_temp.insert(0, "200")
        self.entry_target_temp.grid(row=1, column=1, sticky=tk.W)

        # 数据输入区域
        ttk.Label(self.frame_input, text="时间-温度数据（每行格式：时间 温度）:").grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.text_data = tk.Text(self.frame_input, height=5, width=30)
        self.text_data.grid(row=3, column=0, columnspan=2)
        self.text_data.insert(tk.END, "0 1921\n9 1906\n23 1881\n111 1743")  # 示例数据

        # 计算按钮
        self.btn_calculate = ttk.Button(self.frame_input, text="计算冷却时间", command=self.calculate)
        self.btn_calculate.grid(row=4, column=0, columnspan=2, pady=5)

        # 结果标签
        self.label_result = ttk.Label(self.frame_input, text="")
        self.label_result.grid(row=5, column=0, columnspan=2)

        # 绘图区域
        self.figure = plt.figure(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def parse_input_data(self):
        try:
            T_env = float(self.entry_env_temp.get())
            T_target = float(self.entry_target_temp.get())
        except ValueError:
            return None, None, "环境温度和目标温度必须为数字"

        data_lines = self.text_data.get("1.0", tk.END).strip().split('\n')
        t_list, T_list = [], []
        
        for line in data_lines:
            parts = line.strip().split()
            if len(parts) != 2:
                return None, None, "每行必须包含两个数字（时间 温度）"
            try:
                t_list.append(float(parts[0]))
                T_list.append(float(parts[1]))
            except ValueError:
                return None, None, "无效的数字格式"

        if len(t_list) < 2:
            return None, None, "至少需要两个数据点"
        return t_list, T_list, None

    def calculate(self):
        t_list, T_list, error_msg = self.parse_input_data()
        if error_msg:
            self.label_result.config(text=error_msg, foreground="red")
            return

        try:
            T_env = float(self.entry_env_temp.get())
            T_target = float(self.entry_target_temp.get())
        except ValueError:
            return

        # 数据验证
        valid_temperatures = all(T > T_env for T in T_list)
        if not valid_temperatures:
            self.label_result.config(text="所有温度必须高于环境温度", foreground="red")
            return

        if T_target <= T_env:
            self.label_result.config(text="目标温度必须高于环境温度", foreground="red")
            return

        # 执行线性回归
        try:
            y = np.log(np.array(T_list) - T_env)
            t_array = np.array(t_list)
            coeffs = np.polyfit(t_array, y, 1)
        except Exception as e:
            self.label_result.config(text=f"计算错误: {str(e)}", foreground="red")
            return

        k = -coeffs[0]
        T0 = np.exp(coeffs[1]) + T_env

        if k <= 0:
            self.label_result.config(text="无效的冷却常数，请检查数据", foreground="red")
            return

        # 计算冷却时间
        try:
            ratio = (T_target - T_env) / (T0 - T_env)
            if ratio <= 0:
                self.label_result.config(text="无法达到目标温度", foreground="red")
                return
            t_cool = -np.log(ratio) / k
        except:
            self.label_result.config(text="无法计算冷却时间", foreground="red")
            return

        # 更新结果
        self.label_result.config(
            text=f"预测冷却时间: {round(t_cool)} 分钟 = {t_cool/60:.1f} 小时\n",
            foreground="black"
        )

        # 绘制图形
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用SimHei字体支持中文
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 绘制数据点
        ax.scatter(t_list, T_list, color='red', zorder=5, label='测量数据')
        
        # 生成预测曲线
        t_curve = np.linspace(0, max(max(t_list), t_cool) + 1, 100)
        T_curve = T_env + (T0 - T_env) * np.exp(-k * t_curve)
        ax.plot(t_curve, T_curve, label='预测曲线')
        
        # 绘制目标线
        ax.axhline(T_target, color='green', linestyle='--', label='目标温度')
        ax.axvline(t_cool, color='blue', linestyle=':', label='预测时间')
        
        ax.set_xlabel('时间 (单位)')
        ax.set_ylabel('温度 (℃)')
        ax.set_title('温度冷却曲线')
        ax.grid(True)
        ax.legend()

        plt.tight_layout()
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CoolingPredictorApp(root)
    root.mainloop()