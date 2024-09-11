#!/usr/bin/env python3
import os
import json5  # type: ignore #ignore
import json
import argparse
import re

def get_vcasb_value(config_file_path, reg):
    """从 scan_config.json5 中获取第 reg 个 VCASB 值"""
    with open(config_file_path, 'r') as f:
        config_data = json5.load(f)
    vcasb_values = config_data['moss_dac_settings']['*']['VCASB']
    return vcasb_values[reg]

def get_thr_value(result_file_path, hfunit, reg):
    """从 analysis_result.json5 中获取第 reg 个 Threshold average per region 值"""
    with open(result_file_path, 'r') as f:
        result_data = json5.load(f)
    thr_values = result_data[hfunit]["Threshold average per region"]
    return thr_values[reg]

def find_region_directory(base_directory, hfunit, reg):
    """寻找符合 ScanCollection_*_{hfunit}_reg{reg} 模式的文件夹"""
    pattern = rf'ScanCollection_.*_{hfunit}_reg{reg}$'
    for folder in os.listdir(base_directory):
        if re.match(pattern, folder):
            return os.path.join(base_directory, folder)
    return None

def process_region(moss_name, hfunit, reg, base_directory):
    """处理单个 region，获取所有 VCASB 和 THR 值"""
    vcasb_thr_pairs = []
    
    region_directory = find_region_directory(base_directory, hfunit, reg)
    if not region_directory:
        print(f"Region directory for reg{reg} not found.")
        return [], []
    
    folders = [f for f in os.listdir(region_directory) if os.path.isdir(os.path.join(region_directory, f))]
    
    for folder in folders:
        config_file_path = os.path.join(region_directory, folder, 'config', 'scan_config.json5')
        result_file_path = os.path.join(region_directory, folder, 'analysis', 'analysis_result.json5')
        
        if os.path.exists(config_file_path) and os.path.exists(result_file_path):
            vcasb_value = get_vcasb_value(config_file_path, reg)
            thr_value = get_thr_value(result_file_path, hfunit, reg)
            vcasb_thr_pairs.append((vcasb_value, thr_value))
    
    # 按照 VCASB 值排序
    vcasb_thr_pairs.sort(key=lambda pair: pair[0])
    
    # 分离出排序后的 VCASB 和 THR
    vcasb_values = [pair[0] for pair in vcasb_thr_pairs]
    thr_values = [pair[1] for pair in vcasb_thr_pairs]
    
    return vcasb_values, thr_values

def main(moss_name, hfunit):
    base_directory = f"/Users/wangchunzheng/works/moss_tool/data/2024-08_PS_II/MOSS_TEST_RESULTS/{moss_name}/ThresholdScan"
    output_directory = f"/Users/wangchunzheng/works/moss_tool/analysis/json_files/{moss_name}/{hfunit}/"
    os.makedirs(output_directory, exist_ok=True)
    
    output_json = {}
    
    for reg in range(4):  # reg从0到3
        vcasb_values, thr_values = process_region(moss_name, hfunit, reg, base_directory)
        if vcasb_values and thr_values:
            output_json[str(reg)] = {  # 将键命名为字符串格式的区域索引
                "VCASB": vcasb_values,
                "thr": thr_values
            }
    
    output_filepath = os.path.join(output_directory, f"{moss_name}_{hfunit}_thr.json")
    with open(output_filepath, 'w') as f:
        json.dump(output_json, f, indent=4)
    
    print(f"JSON file {output_filepath} has been created successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate THR JSON file for MOSS and babyMOSS tests.")
    parser.add_argument('hfunit', choices=['t7', 't6', 'b4', 'bb', 'tb'], help='HFUnit (e.g., t7, t6, b4, bb, tb)')
    parser.add_argument('moss_name', choices=['MOSS-2_W02F4', 'MOSS-3_W08B6', 'babyMOSS-2_3_W04E2', 'babyMOSS-2_3_W24B5', 'babyMOSS-2_2_W21D4'], help='MOSS Name (e.g., MOSS-2_W02F4, babyMOSS-2_3_W04E2)')
    args = parser.parse_args()
    
    main(args.moss_name, args.hfunit)