import ROOT  # type: ignore
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import json

print("Script started")  # 确认脚本开始运行

# 设置要绘制的bin数量
num_bins = 16  # 包括ALPIDE内容

# 打开ROOT文件
root_file = ROOT.TFile.Open("filtered_histograms_MOSS-3_W08B6_b4_region0.root")
if not root_file or root_file.IsZombie():
    print("Error: Cannot open ROOT file.")
else:
    print("ROOT file opened successfully.")

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

if not hist_info:
    print("Error: No histograms found in the ROOT file matching the pattern.")
else:
    print(f"Found {len(hist_info)} histograms in the ROOT file.")

# 按照VCASB值排序
hist_info.sort()

# 提取排序后的直方图名称和对应的VCASB值
hist_names = [info[1] for info in hist_info]
vcasb_values = [info[0] for info in hist_info]

# 选择三个特定的VCASB值：开头的、中间的和结尾的
selected_vcasb_indices = [0, len(vcasb_values) // 2, len(vcasb_values) - 1]

# 定义更柔和的颜色列表，调整大小以适应实际绘制的直方图数量
colors = plt.cm.RdYlBu(np.linspace(0, 1, len(selected_vcasb_indices)))  # 使用更柔和的颜色

# 定义柱状图的宽度
bar_width = 0.35 / (len(selected_vcasb_indices) + 1)  # 调整宽度以确保所有柱状图能并排显示并有空隙

# 加载JSON文件
try:
    with open("shape_raw_frequency_ALPIDE.json", "r") as json_file:
        alpide_data = json.load(json_file)
        print("ALPIDE JSON file loaded successfully.")
except FileNotFoundError:
    print("Error: ALPIDE JSON file not found.")
    alpide_data = []

# 提取并归一化所有ALPIDE的内容
total_alpide_content = sum(item[1] for item in alpide_data)
if total_alpide_content > 0:
    normalized_alpide_data = [(str(int(item[0])), item[1] / total_alpide_content) for item in alpide_data]
else:
    print("Warning: ALPIDE data total content is zero or negative.")
    normalized_alpide_data = []

# 提取前16个bin labels和contents
alpide_labels = [item[0] for item in normalized_alpide_data[:num_bins]]
alpide_contents = [item[1] for item in normalized_alpide_data[:num_bins]]

# 打印ALPIDE的bin标签和归一化后的内容，用于QA
print("ALPIDE Data (First 16 Bins - Normalized):")
for label, content in zip(alpide_labels, alpide_contents):
    print(f"Bin {label}: {content}")

# 创建绘图区域
fig, ax = plt.subplots(figsize=(14, 8))

# 绘制ALPIDE数据，颜色设置为黑色
for i, (label, content) in enumerate(zip(alpide_labels, alpide_contents)):
    rect = patches.Rectangle((i - bar_width / 2, 0), bar_width, content, edgecolor='black', facecolor='black', label="ALPIDE" if i == 0 else "")
    #rect = patches.Rectangle((i - bar_width / 2, 0), bar_width, content, edgecolor='black', facecolor='white', hatch='///', label="ALPIDE" if i == 0 else "")
    ax.add_patch(rect)

# 遍历选定的三个直方图，绘制每个直方图的柱状图
for idx, i in enumerate(selected_vcasb_indices):  # 只绘制选定的三个VCASB值
    hist_name = hist_names[i]
    hist = root_file.Get(hist_name)
    if not hist:
        print(f"Warning: Unable to find histogram: {hist_name}")
        continue

    # 获取MOSS直方图中的bin标签
    moss_bin_labels = [hist.GetXaxis().GetBinLabel(j) for j in range(1, hist.GetNbinsX() + 1)]

    # 归一化处理
    total_content = sum(hist.GetBinContent(j) for j in range(1, hist.GetNbinsX() + 1))
    print(f"\nVCASB {vcasb_values[i]}: Total content = {total_content}")  # QA: 打印总内容

    bin_contents = []
    if total_content > 0:
        for alpide_label in alpide_labels:
            # 寻找与ALPIDE标签匹配的MOSS标签
            if alpide_label in moss_bin_labels:
                bin_index = moss_bin_labels.index(alpide_label) + 1  # +1 因为ROOT的bin从1开始
                content = hist.GetBinContent(bin_index) / total_content
            else:
                content = 0
            bin_contents.append(content)
    else:
        bin_contents = [0 for _ in alpide_labels]

    # 打印MOSS的bin标签和重新排列后的内容，用于QA
    print(f"VCASB {vcasb_values[i]} MOSS Bin Contents (Matched to ALPIDE Bins):")
    for label, content in zip(alpide_labels, bin_contents):
        print(f"Bin {label}: {content}")  # 打印所有内容，包括零值

    # 绘制直方图的柱状图，确保与ALPIDE的柱状图对齐，并增加空隙
    plt.bar(np.arange(len(bin_contents)) + (idx + 1) * bar_width * 1., bin_contents, width=bar_width, label=f"VCASB {vcasb_values[i]}", color=colors[idx])

# 设置对数纵轴
plt.yscale("log")

# 设置标签和标题
plt.xlabel("Shape")
plt.ylabel("Frequency(%)")
plt.title(f"Normalized Histogram Distribution for Selected VCASB Values (First {num_bins} Bins)")
plt.xticks(np.arange(len(alpide_labels)) + bar_width * len(selected_vcasb_indices), alpide_labels)
plt.legend(loc="best", fontsize='small', ncol=2)

# 调整布局并显示图形
plt.tight_layout()
plt.show()

# 关闭ROOT文件
root_file.Close()
print("Script finished")  # 确认脚本结束