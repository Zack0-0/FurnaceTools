# 作者：Zack
# 日期：2025/3/13
# 本程序包含两个小工具：炉子冷却时间预测计算器和工艺配方升温曲线生成器

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

class CoolingPredictorApp:
    def __init__(self, master):
        self.master = master
        master.title("冷却时间预测")

        style = ttk.Style()
        style.configure('.', font=('微软雅黑', 10))

        # 输入组件
        self.frame_input = ttk.Frame(master)
        self.frame_input.pack(padx=10, pady=10, fill=tk.X)

        # 环境温度
        ttk.Label(self.frame_input, text="环境温度 (℃):").grid(row=0, column=0, sticky=tk.W)
        self.entry_env_temp = ttk.Entry(self.frame_input)
        self.entry_env_temp.insert(0, "8")
        self.entry_env_temp.grid(row=0, column=1, sticky=tk.W)

        # 目标温度
        ttk.Label(self.frame_input, text="目标温度 (℃):").grid(row=1, column=0, sticky=tk.W)
        self.entry_target_temp = ttk.Entry(self.frame_input)
        self.entry_target_temp.insert(0, "80")
        self.entry_target_temp.grid(row=1, column=1, sticky=tk.W)

        # 数据输入区域
        ttk.Label(self.frame_input, text="时间-温度数据（每行格式：时间(小时:分钟) 温度）:").grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.text_data = tk.Text(self.frame_input, height=5, width=30)
        self.text_data.grid(row=3, column=0, columnspan=2)
        self.text_data.insert(tk.END, "17:52 1921\n18:01 1906\n18:15 1881\n19:43 1743\n21:16 1622")  # 示例数据

        # 计算按钮
        self.btn_calculate = ttk.Button(self.frame_input, text="计算冷却时间", command=self.calculate)
        self.btn_calculate.grid(row=4, column=0, columnspan=2, pady=5)

        # 结果标签
        self.label_result = ttk.Label(self.frame_input, text="")
        self.label_result.grid(row=5, column=0, columnspan=2)

        # 开始日期
        ttk.Label(self.frame_input, text="开始日期 (月-日):").grid(row=0, column=2, sticky=tk.W)
        self.entry_start_date = ttk.Entry(self.frame_input)
        self.entry_start_date.insert(0, "03-13")
        self.entry_start_date.grid(row=0, column=3, sticky=tk.W)

        # 绘图区域
        self.figure = plt.figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def parse_input_data(self):
        try:
            T_env = float(self.entry_env_temp.get())
            T_target = float(self.entry_target_temp.get())
            start_date_str = self.entry_start_date.get()
            start_month, start_day = map(int, start_date_str.split('-'))
        except ValueError:
            return None, None, None, "环境温度、目标温度和开始日期必须为数字"

        data_lines = self.text_data.get("1.0", tk.END).strip().split('\n')
        t_list, T_list = [], []
        start_time = None
        
        for line in data_lines:
            parts = line.strip().split()
            if len(parts) != 2:
                return None, None, None, "每行必须包含两个数字（时间 温度）"
            try:
                time_str = parts[0]
                hours, minutes = map(int, time_str.split(':'))
                total_minutes = hours * 60 + minutes
                if start_time is None:
                    start_time = datetime.now().replace(month=start_month,day=start_day,hour=hours, minute=minutes, second=0, microsecond=0)
                t_list.append(total_minutes-start_time.hour*60-start_time.minute)
                T_list.append(float(parts[1]))
            except ValueError:
                return None, None, None, "无效的数字格式"

        if len(t_list) < 2:
            return None, None, None, "至少需要两个数据点"
        return t_list, T_list, start_time, None

    def calculate(self):
        t_list, T_list, start_time, error_msg = self.parse_input_data()
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

        # 计算冷却完成的具体时间
        cool_time = timedelta(minutes=t_cool)
        end_time = start_time + cool_time

        # 更新结果
        self.label_result.config(
            text=f"预测冷却时间: {round(t_cool)} 分钟 = {t_cool/60:.1f} 小时\n"
                 f"冷却完成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
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
        
        # 将X轴时间转换为具体的日期和时间格式
        time_labels = [start_time + timedelta(minutes=tm) for tm in t_curve]
        ax.set_xticks(t_curve[::10])
        ax.set_xticklabels([t.strftime('%m-%d %H:%M') for t in time_labels[::10]], rotation=45, ha='right')

        ax.set_xlabel('时间')
        ax.set_ylabel('温度 (℃)')
        ax.set_title('温度曲线')
        ax.grid(True)
        ax.legend()

        plt.tight_layout()
        
        self.canvas.draw()


class TemperatureCurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("升温曲线生成")

        # 设置字体
        self.default_font = ("Microsoft YaHei", 10)

        # 创建表格输入区域
        self.create_input_table()

        # 创建按钮区域
        self.create_buttons()

        # 创建图表区域
        self.create_plot_area()

    def create_input_table(self):
        # 表格标题
        self.table_frame = ttk.LabelFrame(self.root, text="工艺配方输入")
        self.table_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # 室温输入框
        ttk.Label(self.table_frame, text="室温 (°C)", font=self.default_font).grid(row=0, column=0, padx=5, pady=5)
        self.room_temp_entry = ttk.Entry(self.table_frame, width=10, font=self.default_font)
        self.room_temp_entry.grid(row=0, column=1, padx=5, pady=5)
        self.room_temp_entry.insert(0, "25")  # 默认室温为25度

        # 表头
        headers = ["阶段", "温度 (°C)", "时间 (分钟)", "升温速率 (°C/分钟)"]
        for col, header in enumerate(headers):
            ttk.Label(self.table_frame, text=header, font=self.default_font).grid(row=1, column=col, padx=5, pady=5)

        # 输入框
        self.stage_labels = []
        self.temp_entries = []
        self.time_entries = []
        self.rate_labels = []
        for _ in range(6):  # 默认6个阶段
            self.add_stage()

        # 绑定事件以更新升温速率
        self.room_temp_entry.bind("<KeyRelease>", self.update_rates)
        for temp_entry, time_entry in zip(self.temp_entries, self.time_entries):
            temp_entry.bind("<KeyRelease>", self.update_rates)
            time_entry.bind("<KeyRelease>", self.update_rates)

    def add_stage(self):
        row = len(self.temp_entries) + 2
        stage_label = ttk.Label(self.table_frame, text=f"{row-1}", font=self.default_font)
        stage_label.grid(row=row, column=0, padx=5, pady=5)
        self.stage_labels.append(stage_label)
        temp_entry = ttk.Entry(self.table_frame, width=10, font=self.default_font)
        temp_entry.grid(row=row, column=1, padx=5, pady=5)
        self.temp_entries.append(temp_entry)
        time_entry = ttk.Entry(self.table_frame, width=10, font=self.default_font)
        time_entry.grid(row=row, column=2, padx=5, pady=5)
        self.time_entries.append(time_entry)
        rate_label = ttk.Label(self.table_frame, text="", font=self.default_font)
        rate_label.grid(row=row, column=3, padx=5, pady=5)
        self.rate_labels.append(rate_label)

        temp_entry.bind("<KeyRelease>", self.update_rates)
        time_entry.bind("<KeyRelease>", self.update_rates)

    def remove_stage(self):
        if self.temp_entries:
            self.stage_labels.pop().grid_forget()
            self.temp_entries.pop().grid_forget()
            self.time_entries.pop().grid_forget()
            self.rate_labels.pop().grid_forget()

    def update_rates(self, event=None):
        try:
            room_temp = float(self.room_temp_entry.get())
        except ValueError:
            room_temp = 25  # 如果输入无效，默认室温为25度

        previous_temp = room_temp
        for temp_entry, time_entry, rate_label in zip(self.temp_entries, self.time_entries, self.rate_labels):
            temp = temp_entry.get()
            time = time_entry.get()
            if temp and time:
                try:
                    temp_value = float(temp)
                    time_value = float(time)
                    if time_value != 0:  # 忽略时间为0的阶段
                        rate = (temp_value - previous_temp) / time_value
                        rate_label.config(text=f"{rate:.2f}")
                        previous_temp = temp_value
                    else:
                        rate_label.config(text="")
                except ValueError:
                    rate_label.config(text="")
            else:
                rate_label.config(text="")

    def create_buttons(self):
        # 按钮区域
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        ttk.Button(button_frame, text="生成曲线", command=self.plot_curve).grid(row=0, column=0, padx=5, pady=5)
        # 删除保存配方按钮
        # ttk.Button(button_frame, text="保存配方", command=self.save_recipe).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="加载配方", command=self.load_recipe).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="重置", command=self.reset_entries).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="增加阶段", command=self.add_stage).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="删减阶段", command=self.remove_stage).grid(row=5, column=0, padx=5, pady=5)

    def create_plot_area(self):
        # 图表区域
        plot_frame = ttk.LabelFrame(self.root, text="升温曲线预览")
        plot_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="se")

        # 创建一个Figure和Axes
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_curve(self):
        # 更新升温速率
        self.update_rates()
        
        # 从输入框获取数据
        temps = []
        times = []
        for temp_entry, time_entry in zip(self.temp_entries, self.time_entries):
            temp = temp_entry.get()
            time = time_entry.get()
            if temp and time:
                temp_value = float(temp)
                time_value = float(time)
                if temp_value != 0 or time_value != 0:  # 忽略温度和时间都为0的阶段
                    temps.append(temp_value)
                    times.append(time_value)

        # 清空当前图表
        self.ax.clear()

        # 绘制曲线
        cumulative_time = 0
        try:
            room_temp = float(self.room_temp_entry.get())
        except ValueError:
            room_temp = 25  # 如果输入无效，默认室温为25度

        x = [0]
        y = [room_temp]
        for i in range(len(temps)):
            if i < len(times):
                cumulative_time += times[i]
                x.append(cumulative_time)
                y.append(temps[i])

        self.ax.plot(x, y, marker='o', linestyle='-', color='r')

        # 设置字体属性
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用SimHei字体支持中文
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        self.ax.set_ylim(0, 2000)

        self.ax.set_title("工艺配方升温曲线")
        self.ax.set_xlabel("时间 (分钟)")
        self.ax.set_ylabel("温度 (°C)")

        # 在对应的位置添加文字标注
        previous_temp = None
        for i, (temp, time) in enumerate(zip(temps, times)):
            if temp != 0 and time != 0:
                if temp != previous_temp:  # 只有当当前温度与前一个温度不同时才标注
                    self.ax.text(x[i+1], y[i+1] + 20, f"{temp}°C", fontsize=10, ha='center', va='bottom')
                previous_temp = temp

        # 添加升温速率的标注
        for i, rate_label in enumerate(self.rate_labels):
            rate_text = rate_label.cget("text")
            if rate_text:
                rate = float(rate_text)
                if rate > 0:
                    # 调整va参数为'top'，并增加y轴偏移量
                    self.ax.text(x[i+1], y[i+1] - 40, f"{rate:.1f}°C/min", fontsize=10, ha='center', va='top')

        # 添加网格线
        self.ax.grid(True, linestyle='--', alpha=0.7)

        self.ax.grid(True)

        # 更新图表
        self.canvas.draw()

    def load_recipe(self):
        # 加载配方到输入框
        # 这里可以添加从文件加载的逻辑
        # 示例数据
        sample_recipe = {
            "段1": {"温度": 300, "时间": 30},
            "段2": {"温度": 600, "时间": 30},
            "段3": {"温度": 1000, "时间": 100},
            "段4": {"温度": 1600, "时间": 130},
            "段5": {"温度": 1950, "时间": 175},
            "段6": {"温度": 1950, "时间": 30}
        }

        for i, (temp_entry, time_entry) in enumerate(zip(self.temp_entries, self.time_entries)):
            segment = f"段{i+1}"
            if segment in sample_recipe:
                temp_entry.delete(0, tk.END)
                temp_entry.insert(0, str(sample_recipe[segment]["温度"]))
                time_entry.delete(0, tk.END)
                time_entry.insert(0, str(sample_recipe[segment]["时间"]))
        
        # 加载配方后自动生成曲线
        self.plot_curve()

    def reset_entries(self):
        # 清空所有输入框
        for entry in self.temp_entries + self.time_entries:
            entry.delete(0, tk.END)

if __name__ == "__main__":
    def open_cooling_predictor():
        new_window = tk.Toplevel(root)
        CoolingPredictorApp(new_window)

    def open_temperature_curve():
        new_window = tk.Toplevel(root)
        TemperatureCurveApp(new_window)

    root = tk.Tk()
    root.title("选择功能")
    root.geometry("300x200")
      
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(padx=10, pady=10)

    ttk.Label(main_frame, text="请选择要使用的功能:", font=("微软雅黑", 12)).pack(pady=10)

    ttk.Button(main_frame, text="炉子冷却时间预测计算器", command=open_cooling_predictor,width=80).pack(pady=10)
    ttk.Button(main_frame, text="工艺配方升温曲线生成器", command=open_temperature_curve,width=80).pack(pady=10)


    root.mainloop()