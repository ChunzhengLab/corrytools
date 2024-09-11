import ROOT  # type: ignore
import os
import glob
import json
import argparse
from collections import defaultdict

def load_top_keys_from_json(json_file, top_n=20):
    print(f"加载JSON文件: {json_file}")
    with open(json_file, "r") as f:
        data = json.load(f)
    top_keys = [str(entry[0]) for entry in data[:top_n]]
    print(f"从JSON文件加载的前{top_n}个label: {top_keys}")
    return top_keys

def create_filtered_histogram(original_hist, top_keys, hist_name):
    print(f"创建新的直方图: {hist_name}")
    # 创建一个新的 TH1D 直方图，bin 数量为 top_keys 的数量
    new_hist = ROOT.TH1D(hist_name, hist_name, len(top_keys), 0, len(top_keys))

    # 为新直方图设置 bin labels
    for idx, key in enumerate(top_keys):
        new_hist.GetXaxis().SetBinLabel(idx + 1, key)

    # 填充新直方图
    for bin_idx in range(1, original_hist.GetNbinsX() + 1):
        bin_label = original_hist.GetXaxis().GetBinLabel(bin_idx)
        bin_content = original_hist.GetBinContent(bin_idx)
        print(f"处理 bin label: {bin_label}, 内容: {bin_content}")
        if bin_label in top_keys:
            new_bin_idx = top_keys.index(bin_label) + 1
            new_hist.SetBinContent(new_bin_idx, bin_content)
            print(f"将 bin {bin_label} 内容设置为 {bin_content} 到新的直方图的 bin {new_bin_idx}")

    print(f"完成直方图: {hist_name}")
    return new_hist

def process_files(hf_unit, moss_name, region):
    print(f"开始处理: hf_unit={hf_unit}, moss_name={moss_name}, region={region}")
    search_path = f"/Users/wangchunzheng/works/moss_tool/analysis/output/{moss_name}_{hf_unit}_region{region}_VCASB*/analysis.root"
    print(f"搜索路径: {search_path}")
    root_files = glob.glob(search_path)
    
    if not root_files:
        print(f"未找到任何匹配的ROOT文件，请检查路径: {search_path}")
        return
    
    print(f"找到 {len(root_files)} 个ROOT文件")

    # 读取 JSON 文件中的前 20 个 key
    json_file_path = "/Users/wangchunzheng/works/moss_tool/analysis/cluster_shape/shape_raw_frequency_ALPIDE.json"
    top_keys = load_top_keys_from_json(json_file_path)

    # 对文件按照 VCASB 值排序
    root_files = sorted(root_files, key=lambda x: int(x.split("_VCASB")[-1].split("/")[0]))

    # 打开一个新的 ROOT 文件来存储结果
    output_root_file = ROOT.TFile(f"filtered_histograms_{moss_name}_{hf_unit}_region{region}.root", "RECREATE")

    # 遍历所有找到的 ROOT 文件
    for root_file in root_files:
        print(f"处理文件: {root_file}")
        vcasb_value = root_file.split("_VCASB")[-1].split("/")[0]  # 提取 VCASB 值
        print(f"提取到的VCASB值: {vcasb_value}")
        file = ROOT.TFile.Open(root_file)
        if not file or file.IsZombie():
            print(f"无法打开文件: {root_file}")
            continue

        # 构建直方图路径
        hist_path = f"AnalysisDUT/MOSS_reg{region}_3/clusterShapeAssociated"
        print(f"尝试读取直方图路径: {hist_path}")
        original_hist = file.Get(hist_path)
        if not original_hist:
            print(f"无法找到直方图: {hist_path} in {root_file}")
            file.Close()
            continue

        print(f"成功读取直方图: {hist_path}，开始创建过滤后的直方图")
        # 创建新的过滤后的直方图
        new_hist_name = f"{moss_name}_{hf_unit}_region{region}_VCASB{vcasb_value}"
        filtered_hist = create_filtered_histogram(original_hist, top_keys, new_hist_name)
        
        # 将新直方图写入输出 ROOT 文件
        output_root_file.cd()
        filtered_hist.Write()
        print(f"已将过滤后的直方图写入文件: {new_hist_name}")

        file.Close()

    output_root_file.Close()
    print(f"所有结果已保存到 filtered_histograms_{moss_name}_{hf_unit}_region{region}.root")

if __name__ == "__main__":
    # 解析输入参数
    parser = argparse.ArgumentParser(description="Process ROOT files and create filtered histograms.")
    parser.add_argument("hf_unit", choices=["t7", "t6", "b4"], help="The HF unit to process.")
    parser.add_argument("moss_name", help="The name of the MOSS chip to process.")
    parser.add_argument("region", type=int, choices=[0, 1, 2, 3], help="The region to process.")
    args = parser.parse_args()

    # 处理文件并生成新的直方图
    process_files(args.hf_unit, args.moss_name, args.region)