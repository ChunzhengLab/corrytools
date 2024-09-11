import argparse
import os
import json
import json5  # 用于读取 JSON5 文件

def find_last_vcasb_value(data_json, region):
    """在指定的 region 中找到最后一个 eff 小于 99 的 VCASB 值"""
    vcasb_value = None
    if str(region) not in data_json:
        print(f"Warning: No data found for region {region} in the data JSON file.")
        return None
    for vcasb, eff in zip(data_json[str(region)]["VCASB"], data_json[str(region)]["eff"]):
        if eff < 99:
            vcasb_value = vcasb
    return vcasb_value

def find_scan_config_path(base_dir, moss_name, hf_unit, region, target_vcasb):
    """寻找匹配的 scan_config.json5 文件路径"""
    scan_dir = os.path.join(base_dir, moss_name, f"FakeHitRateScan")
    
    # 遍历所有匹配的文件夹
    for root, dirs, files in os.walk(scan_dir):
        # 仅匹配包含正确 hf_unit 和 region 的文件夹
        if f"{hf_unit}_reg{region}" in root:
            for file in files:
                if file == "scan_config.json5":
                    scan_config_path = os.path.join(root, file)
                    with open(scan_config_path, 'r') as f:
                        config_data = json5.load(f)
                        if target_vcasb in config_data['moss_dac_settings']['*']['VCASB']:
                            return scan_config_path
    return None

def extract_frequent_pixels(analysis_result_path, hf_unit, region):
    """从 analysis_result.json5 文件中提取与指定 region 匹配的 MaskedPixels 数据"""
    with open(analysis_result_path, 'r') as f:
        result_data = json5.load(f)
    
    # 提取 hf_unit 下的 MaskedPixels 数据
    all_pixels = result_data.get(hf_unit, {}).get("MaskedPixels", [])
    
    # 过滤只包含指定 region 的像素数据，并返回 [col, row] 格式
    filtered_pixels = [[pixel[1], pixel[2]] for pixel in all_pixels if pixel[0] == region]
    
    return filtered_pixels

def save_combined_json(masked_pixels_data, moss_name, hf_unit, output_dir):
    """将所有区域的 MaskedPixels 数据合并并保存为一个 JSON 文件"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建文件名
    output_json_path = os.path.join(output_dir, f"masked_pixel_{moss_name}_{hf_unit}.json")
    
    # 保存为 JSON 文件
    with open(output_json_path, 'w') as f:
        json.dump(masked_pixels_data, f, indent=4)
    
    print(f"Combined MaskedPixels data saved to {output_json_path}")

def save_pixels_to_txt(filtered_pixels, moss_name, hf_unit, region, output_dir):
    """将 MaskedPixels 数据保存为 TXT 文件"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建文件名
    base_filename = os.path.join(output_dir, f"masked_pixel_{moss_name}_{hf_unit}_reg{region}")
    
    # 保存为 TXT 文件
    output_txt_path = f"{base_filename}.txt"
    with open(output_txt_path, 'w') as f:
        for pixel in filtered_pixels:
            f.write(f"p {pixel[0]} {pixel[1]}\n")
    print(f"MaskedPixels data saved to {output_txt_path}")

def main(hf_unit, moss_name, output_dir):
    # 自动推导 data_json 文件路径
    data_json_path = os.path.join("json_files", moss_name, hf_unit, f"{moss_name}_{hf_unit}_eff.json")
    
    # 检查 data_json 文件是否存在
    if not os.path.exists(data_json_path):
        print(f"Data JSON file not found: {data_json_path}")
        return
    
    # 读取 data_json 文件
    with open(data_json_path, 'r') as f:
        data_json = json.load(f)
    
    masked_pixels_data = {hf_unit: {}}

    for region in range(4):
        # 找到最后一个 eff 小于 99 的 VCASB 值
        target_vcasb = find_last_vcasb_value(data_json, region)
        if target_vcasb is None:
            print(f"Warning: No valid VCASB found for region {region}. Saving empty entry.")
            masked_pixels_data[hf_unit][region] = []
            continue
        
        print(f"Found VCASB: {target_vcasb} with efficiency less than 99 for region {region}")
        
        # 基础目录
        base_dir = f"/Users/wangchunzheng/works/moss_tool/data/2024-08_PS_II/MOSS_TEST_RESULTS"
        
        # 寻找匹配的 scan_config.json5 文件路径
        scan_config_path = find_scan_config_path(base_dir, moss_name, hf_unit, region, target_vcasb)
        if scan_config_path is None:
            print(f"Warning: No matching scan_config.json5 file found for VCASB {target_vcasb}. Saving empty entry.")
            masked_pixels_data[hf_unit][region] = []
            continue
        
        print(f"Found matching scan_config.json5 at {scan_config_path}")
        
        # 对应的 analysis_result.json5 文件路径
        analysis_result_path = scan_config_path.replace('/config/scan_config.json5', '/analysis/analysis_result.json5')
        
        # 提取 MaskedPixels 数据
        frequent_pixels = extract_frequent_pixels(analysis_result_path, hf_unit, region)
        
        if not frequent_pixels:
            print(f"Warning: No MaskedPixels found for region {region} in {analysis_result_path}. Saving empty entry.")
            masked_pixels_data[hf_unit][region] = []
            continue
        
        print(f"Extracted MaskedPixels for region {region}: {frequent_pixels}")
        
        # 保存 MaskedPixels 到合并的数据结构
        masked_pixels_data[hf_unit][region] = frequent_pixels
        
        # 额外保存为 TXT 文件
        save_pixels_to_txt(frequent_pixels, moss_name, hf_unit, region, output_dir)
    
    # 保存所有区域的 MaskedPixels 数据为一个合并的 JSON 文件
    save_combined_json(masked_pixels_data, moss_name, hf_unit, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a combined masked_pixel.json and individual masked_pixel.txt files based on efficiency and VCASB.")
    parser.add_argument("hf_unit", type=str, help="HF Unit (e.g., t7, t6, b4, bb, tb)")
    parser.add_argument("moss_name", type=str, help="MOSS Name (e.g., MOSS-2_W02F4, MOSS-3_W08B6, babyMOSS-2_3_W04E2)")
    parser.add_argument("-o", "--output-dir", type=str, default="/Users/wangchunzheng/works/moss_tool/analysis/geometry_update/mask_files/", help="Output directory for the mask files")
    
    args = parser.parse_args()
    
    main(args.hf_unit, args.moss_name, args.output_dir)

