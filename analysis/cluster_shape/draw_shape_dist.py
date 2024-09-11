import ROOT  # type: ignore
import numpy as np
import matplotlib.pyplot as plt
import re

# 设置要绘制的bin数量
num_bins = 8  # 例如，只绘制前7个bin

# 打开ROOT文件
root_file = ROOT.TFile.Open("filtered_histograms_MOSS-3_W08B6_b4_region0.root")

# 定义正则表达式来匹配直方图名称中的VCASB值
pattern = re.compile(r"VCASB(\d+)")

# 初始化一个列表来存储（VCASB值，直方图名称）的元组
hist_info = []

# 获取ROOT文件中的所有键（即对象名称）
for key in root_file.GetListOfKeys():
    hist_name = key.GetName()
    match = pattern.search(hist_name)
    if match:
        vcasb_value = int(match.group(1))
        hist_info.append((vcasb_value, hist_name))

# 按照VCASB值排序
hist_info.sort()

# 提取排序后的直方图名称和对应的VCASB值
hist_names = [info[1] for info in hist_info]
vcasb_values = [info[0] for info in hist_info]

# 计算奇数序列的数量
odd_count = len(hist_names) // 2 + (len(hist_names) % 2)

# 定义颜色列表，调整大小以适应实际绘制的直方图数量
colors = plt.cm.jet(np.linspace(0, 1, odd_count))

# 设置柱状图的宽度
bar_width = 0.8 / odd_count  # 使得所有直方图能并排显示

# 创建绘图区域
plt.figure(figsize=(12, 8))

# 遍历所有直方图，绘制每个直方图的柱状图，只绘制奇数序列的直方图
for i in range(0, len(hist_names), 2):  # 只考虑序列为奇数的直方图
    hist_name = hist_names[i]
    hist = root_file.Get(hist_name)
    if not hist:
        print(f"无法找到直方图: {hist_name}")
        continue

    # 归一化处理
    total_content = sum(hist.GetBinContent(j) for j in range(1, hist.GetNbinsX() + 1))
    if total_content > 0:
        bin_contents = [hist.GetBinContent(j) / total_content for j in range(1, min(hist.GetNbinsX() + 1, num_bins + 1))]
    else:
        bin_contents = [0 for j in range(1, min(hist.GetNbinsX() + 1, num_bins + 1))]

    # 获取原始的x轴标签
    bin_labels = [hist.GetXaxis().GetBinLabel(j) for j in range(1, min(hist.GetNbinsX() + 1, num_bins + 1))]

    # 绘制直方图的柱状图
    plt.bar(np.arange(len(bin_contents)) + (i // 2) * bar_width, bin_contents, width=bar_width, label=f"VCASB {vcasb_values[i]}", color=colors[i // 2])

# 设置对数纵轴
plt.yscale("log")

# 设置标签和标题
plt.xlabel("Shape")
plt.ylabel("Frequency(%) (log scale)")
plt.title(f"Normalized Histogram Distribution for Odd-Indexed VCASB Values (First {num_bins} Bins)")
plt.xticks(np.arange(len(bin_labels)) + bar_width * (odd_count - 1) / 2, bin_labels)
plt.legend(loc="best", fontsize='small', ncol=2)

# 调整布局并显示图形
plt.tight_layout()
plt.show()

# 关闭ROOT文件
root_file.Close()
