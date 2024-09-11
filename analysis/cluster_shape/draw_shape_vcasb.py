import ROOT  # type: ignore
import numpy as np
import matplotlib.pyplot as plt
import re
import argparse

def plot_cluster_shape_vs_vcasb(hf_unit, moss_name, region):
    # 构建ROOT文件路径
    root_file_path = f"filtered_histograms_{moss_name}_{hf_unit}_region{region}.root"
    
    # 打开ROOT文件
    root_file = ROOT.TFile.Open(root_file_path)
    if not root_file or root_file.IsZombie():
        print(f"Error: Cannot open ROOT file: {root_file_path}")
        return

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

    # 定义颜色列表
    colors = plt.cm.RdYlBu(np.linspace(0, 1, 7))  # 使用plasma颜色

    # 创建绘图区域
    plt.figure(figsize=(12, 8))

    # 存储每个bin的内容变化和label
    bin_contents = {i: [] for i in range(1, 8)}  # 第1到第7个bin
    bin_labels = {}

    # 遍历所有直方图，提取每个bin的内容和label
    for hist_name in hist_names:
        hist = root_file.Get(hist_name)
        if not hist:
            print(f"无法找到直方图: {hist_name}")
            continue

        # 归一化处理
        total_content = sum(hist.GetBinContent(j) for j in range(1, hist.GetNbinsX() + 1))
        if total_content > 0:
            for bin_idx in range(1, 8):  # 只考虑前7个bin
                normalized_content = hist.GetBinContent(bin_idx) / total_content
                bin_contents[bin_idx].append(normalized_content)
                # 存储 bin label
                if bin_idx not in bin_labels:
                    bin_labels[bin_idx] = hist.GetXaxis().GetBinLabel(bin_idx)
        else:
            for bin_idx in range(1, 8):
                bin_contents[bin_idx].append(0)

    # 绘制每个bin的内容随VCASB变化的曲线
    for bin_idx in range(1, 8):
        plt.plot(vcasb_values, bin_contents[bin_idx], label=f"{bin_labels[bin_idx]}", color=colors[bin_idx-1])

    # 设置对数纵轴（如果需要的话）
    # plt.yscale("log")

    # 设置标签和标题
    plt.xlabel("VCASB")
    plt.ylabel("Fraction of Cluster Shape (%)")
    plt.title("Cluster Shape vs. VCASB")
    plt.legend(loc="best")

    # 加上网格线
    plt.grid()

    # 添加文字，标注MOSS, HF Unit, Region
    plt.text(0.05, 0.95, f"MOSS: {moss_name}\nHF Unit: {hf_unit}\nRegion: {region}", 
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')

    # 调整布局并显示图形
    plt.tight_layout()
    plt.show()

    # 关闭ROOT文件
    root_file.Close()

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Plot Cluster Shape vs. VCASB")
    parser.add_argument("hf_unit", type=str, help="HF unit identifier (e.g., 08B6)")
    parser.add_argument("moss_name", type=str, help="MOSS name (e.g., MOSS-3)")
    parser.add_argument("region", type=int, help="Region number (e.g., 3)")

    args = parser.parse_args()

    # 调用绘图函数
    plot_cluster_shape_vs_vcasb(args.hf_unit, args.moss_name, args.region)