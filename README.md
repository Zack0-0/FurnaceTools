# 温度冷却预测与工艺配方升温曲线工具

这是一个包含两个功能的工具集，用于温度冷却预测和工艺配方升温曲线生成。以下是每个功能的详细介绍和使用说明。

## 1. 功能概述

### 1.1 炉子冷却时间预测计算器
该工具用于预测炉子从初始温度冷却到目标温度所需的时间。它通过线性回归拟合温度随时间的变化曲线，并计算冷却时间。

### 1.2 工艺配方升温曲线生成器
该工具用于生成工艺配方的升温曲线。用户可以输入不同阶段的温度和时间，工具会自动生成升温曲线，并显示升温速率。

## 2. 使用方法

### 2.1 安装依赖
在运行程序之前，请确保安装了以下依赖库：
```bash
pip install tkinter numpy matplotlib
```

### 2.2 运行程序
运行程序后，会弹出一个主窗口，用户可以选择要使用的功能。

#### 2.2.1 炉子冷却时间预测计算器
1. 输入环境温度和目标温度。
2. 在数据输入区域输入时间-温度数据，每行格式为“时间 温度”。
3. 点击“计算冷却时间”按钮，程序会显示预测的冷却时间和冷却完成时间，并绘制温度冷却曲线。

#### 2.2.2 工艺配方升温曲线生成器
1. 输入室温。
2. 在表格中输入每个阶段的温度和时间。**点击加载配方，会加载默认配方**。
3. 点击“生成曲线”按钮，程序会显示升温曲线，并标注每个阶段的温度和升温速率。

## 3. 示例数据

### 3.1 炉子冷却时间预测
输入以下数据：
- 环境温度：`8`
- 目标温度：`80`
- 数据输入区域：
  ```
  17:52 1921
  18:01 1906
  18:15 1881
  19:43 1743
  21:16 1622
  ```
程序会计算冷却时间并绘制曲线。

### 3.2 工艺配方升温曲线
输入以下数据：
- 室温：`25`
- 阶段1：温度 `300`，时间 `30`
- 阶段2：温度 `600`，时间 `30`
- 阶段3：温度 `1000`，时间 `100`
- 阶段4：温度 `1600`，时间 `130`
- 阶段5：温度 `1950`，时间 `175`
- 阶段6：温度 `1950`，时间 `30`
程序会生成升温曲线并显示。

## 4. 注意事项
- 输入数据时，请确保格式正确，避免输入无效数据。
- 如果程序提示错误，请根据提示信息检查输入数据。
- 该工具仅用于预测和生成曲线，实际应用中可能会受到多种因素的影响。

## 5. 文件结构
- `cooling_predictor2.py`：炉子冷却时间预测计算器。
- `TempPlot.py`：工艺配方升温曲线生成器。
- `all_in_one.py`：集成两个工具的主程序。
- `cooling_predictor.py`：早期版本的冷却时间预测工具。
