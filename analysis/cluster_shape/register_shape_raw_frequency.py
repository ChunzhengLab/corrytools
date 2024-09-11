import ROOT  # type: ignore
import glob
import argparse
from collections import defaultdict
import json

def process_histogram(hist, global_label_freq):
    # 获取总 content
    total_content = sum(hist.GetBinContent(i) for i in range(1, hist.GetNbinsX() + 1))

    # 遍历所有 bin
    for bin_idx in range(1, hist.GetNbinsX() + 1):
        bin_label = hist.GetXaxis().GetBinLabel(bin_idx)
        bin_content = hist.GetBinContent(bin_idx)

        # 计算该 bin 的频率
        if total_content > 0:
            frequency_for_thisLabel = bin_content / total_content
        else:
            frequency_for_thisLabel = 0

        # 累加到全局 label 频率表中
        if bin_label:
            global_label_freq[bin_label] += frequency_for_thisLabel

def normalize_frequencies(global_label_freq):
    total_frequency = sum(global_label_freq.values())
    if total_frequency > 0:
        for label in global_label_freq:
            global_label_freq[label] /= total_frequency

def process_root_files(chip_name, search_path):
    # 定义一个字典存储所有 label 的频率
    global_label_freq = defaultdict(float)

    # 获取所有匹配的 root 文件路径
    root_files = glob.glob(search_path)

    # 定义直方图路径列表
    histogram_paths = []
    if chip_name == "MOSS":
        histogram_paths = [
            "ClusteringSpatial/MOSS_reg0_3/clusterPixelMatrix",
            "ClusteringSpatial/MOSS_reg1_3/clusterPixelMatrix",
            "ClusteringSpatial/MOSS_reg2_3/clusterPixelMatrix",
            "ClusteringSpatial/MOSS_reg3_3/clusterPixelMatrix"
        ]
    elif chip_name == "ALPIDE":
        histogram_paths = [
            "ClusteringSpatial/ALPIDE_0/clusterPixelMatrix",
            "ClusteringSpatial/ALPIDE_1/clusterPixelMatrix",
            "ClusteringSpatial/ALPIDE_2/clusterPixelMatrix",
            "ClusteringSpatial/ALPIDE_4/clusterPixelMatrix",
            "ClusteringSpatial/ALPIDE_5/clusterPixelMatrix",
            "ClusteringSpatial/ALPIDE_6/clusterPixelMatrix",
        ]

    # 遍历所有的 root 文件
    for root_file in root_files:
        # 打开 ROOT 文件
        file = ROOT.TFile.Open(root_file)
        if not file or file.IsZombie():
            print(f"无法打开文件: {root_file}")
            continue

        # 遍历所有指定的直方图路径
        for hist_path in histogram_paths:
            # 读取指定的 TH1I 直方图
            histogram = file.Get(hist_path)
            if not histogram:
                print(f"无法找到直方图: {hist_path} in {root_file}")
                continue

            # 处理该直方图，更新全局 label 频率表
            process_histogram(histogram, global_label_freq)

        # 关闭 ROOT 文件
        file.Close()

    # 归一化全局 label 频率
    normalize_frequencies(global_label_freq)

    # 将全局 label 频率表转换为列表并排序
    sorted_label_freq = sorted(global_label_freq.items(), key=lambda x: x[1], reverse=True)

    return sorted_label_freq

def merge_and_normalize_frequencies(freq_list_1, freq_list_2):
    # 合并两个频率列表
    merged_freq = defaultdict(float)

    for label, freq in freq_list_1:
        merged_freq[label] += freq

    for label, freq in freq_list_2:
        merged_freq[label] += freq

    # 归一化合并后的频率
    normalize_frequencies(merged_freq)

    # 返回排序后的频率列表
    return sorted(merged_freq.items(), key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    # 解析输入参数
    parser = argparse.ArgumentParser(description="Process ROOT files and calculate label frequencies.")
    parser.add_argument("chip_name", choices=["MOSS", "ALPIDE", "all"], help="The name of the chip to process or 'all' to process both.")
    args = parser.parse_args()

    # 定义搜索路径
    search_path = "/Users/wangchunzheng/works/moss_tool/analysis/output/*/analysis.root"

    if args.chip_name == "all":
        # 处理 MOSS 和 ALPIDE，分别获取排序后的 label 频率列表
        moss_sorted_label_freq = process_root_files("MOSS", search_path)
        alpide_sorted_label_freq = process_root_files("ALPIDE", search_path)

        # 合并并再次归一化
        final_sorted_label_freq = merge_and_normalize_frequencies(moss_sorted_label_freq, alpide_sorted_label_freq)
    else:
        # 处理指定的芯片类型
        final_sorted_label_freq = process_root_files(args.chip_name, search_path)

    # 保存结果为 JSON 文件
    output_json_path = f"shape_raw_frequency_{args.chip_name}.json"
    with open(output_json_path, "w") as f:
        json.dump(final_sorted_label_freq, f, indent=4)

    print(f"结果已保存到 {output_json_path}")