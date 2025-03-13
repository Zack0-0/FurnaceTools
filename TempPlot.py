import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TemperatureCurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("工艺配方升温曲线生成器")

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
    root = tk.Tk()
    app = TemperatureCurveApp(root)
    root.mainloop()