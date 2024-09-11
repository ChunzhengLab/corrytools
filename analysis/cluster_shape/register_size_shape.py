import json
import ROOT #type: ignore
import glob
import os
import argparse

# 解析输入参数
parser = argparse.ArgumentParser(description="Process ROOT files and generate a JSON output.")
parser.add_argument("chip_name", choices=["MOSS", "ALPIDE"], help="The name of the chip to process.")
args = parser.parse_args()

# 根据chip_name选择相应的路径列表
if args.chip_name == "MOSS":
    histogram_paths = [
        "ClusteringSpatial/MOSS_reg0_3/clusterPixelMatrix",
        "ClusteringSpatial/MOSS_reg1_3/clusterPixelMatrix",
        "ClusteringSpatial/MOSS_reg2_3/clusterPixelMatrix",
        "ClusteringSpatial/MOSS_reg3_3/clusterPixelMatrix"
    ]
elif args.chip_name == "ALPIDE":
    histogram_paths = [
        "ClusteringSpatial/ALPIDE_0/clusterPixelMatrix",
        "ClusteringSpatial/ALPIDE_1/clusterPixelMatrix",
        "ClusteringSpatial/ALPIDE_2/clusterPixelMatrix",
        "ClusteringSpatial/ALPIDE_4/clusterPixelMatrix",
        "ClusteringSpatial/ALPIDE_5/clusterPixelMatrix",
        "ClusteringSpatial/ALPIDE_6/clusterPixelMatrix",
    ]

# 定义搜索路径
search_path = "/Users/wangchunzheng/works/moss_tool/analysis/output/*/analysis.root"

# 获取所有匹配的root文件路径
root_files = glob.glob(search_path)

# 定义一个字典存储所有文件的cluster size与对应的Uint64编码
all_cluster_map = {}

# 遍历所有的root文件
for root_file in root_files:
    # 打开ROOT文件
    file = ROOT.TFile.Open(root_file)
    if not file or file.IsZombie():
        print(f"无法打开文件: {root_file}")
        continue

    # 遍历所有指定的直方图路径
    for hist_path in histogram_paths:
        # 读取指定的TH1D直方图
        histogram = file.Get(hist_path)
        if not histogram:
            print(f"无法找到直方图: {hist_path} in {root_file}")
            continue

        # 遍历所有bin，提取每个bin的label（假设label为Uint64的字符串表示）
        n_bins = histogram.GetNbinsX()
        for bin_idx in range(1, n_bins + 1):
            bin_label = histogram.GetXaxis().GetBinLabel(bin_idx)

            # 检查bin标签是否为空
            if not bin_label:
                # print(f"警告: {root_file} 中 {hist_path} 的 Bin {bin_idx} 的标签为空，跳过该bin。")
                continue

            # 尝试将label（假设是Uint64字符串）转换为数值
            try:
                decimal_representation = int(bin_label)
            except ValueError:
                print(f"错误: {root_file} 中 {hist_path} 的 Bin {bin_idx} 的标签无法转换为Uint64: {bin_label}")
                continue

            # 从十进制数字恢复布尔矩阵，并计算cluster size
            matrix = [[False for _ in range(8)] for _ in range(8)]
            cluster_size = 0
            for i in range(8):
                for j in range(8):
                    matrix[i][j] = (decimal_representation & (1 << (i * 8 + j))) != 0
                    if matrix[i][j]:
                        cluster_size += 1

            # 使用set来存储不重复的Uint64编码
            if cluster_size not in all_cluster_map:
                all_cluster_map[cluster_size] = set()

            all_cluster_map[cluster_size].add(bin_label)

    # 关闭ROOT文件
    file.Close()

# 将set转换为列表并排序
sorted_all_cluster_map = {k: sorted(list(v)) for k, v in sorted(all_cluster_map.items())}

# 将结果保存为JSON文件
output_json_path = f"size_shape_{args.chip_name}.json"
with open(output_json_path, "w") as f:
    json.dump(sorted_all_cluster_map, f, indent=4)

print(f"所有数据已成功写入 {output_json_path}")