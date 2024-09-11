import argparse
import os
import re
import numpy as np
import json
from ROOT import TFile, TH1

def get_histogram_from_file(file_name, hist_name):
    """从单个文件中获取直方图"""
    f = TFile(file_name, "READ")
    hist = f.Get(hist_name)
    if hist:
        hist.SetDirectory(0)  # 将直方图与文件分离
    f.Close()
    return hist

def add_histograms(file_list, hist_name):
    """将多个文件中的同名直方图相加"""
    hist_sum = None
    for fname in file_list:
        print(f"Processing file: {fname}")  # QA语句：输出正在处理的文件名
        f = TFile(fname, "READ")
        hist = f.Get(hist_name)
        if hist:
            print(f"Found histogram: {hist_name} in {fname}")  # QA语句：确认找到直方图
            if not hist_sum:
                hist_sum = hist.Clone()
                hist_sum.SetDirectory(0)  # 克隆后要将直方图与文件分离
            else:
                hist_sum.Add(hist)
        else:
            print(f"Histogram: {hist_name} not found in {fname}")  # QA语句：如果未找到直方图，输出警告信息
        f.Close()
    return hist_sum

def get_values_from_file(file_list, plane, vcasb, no_add):
    try:
        print(f"Total number of ROOT files to process: {len(file_list)}")  # QA语句：输出要处理的文件数量

        if no_add:
            # 如果设置了 no_add 参数，仅处理第一个文件
            print("No addition mode enabled, using the first file only.")
            file_list = [file_list[0]]

        # 获取直方图，可能进行叠加，也可能仅取第一个文件
        residualsX_hist = add_histograms(file_list, f"AnalysisDUT/{plane}/global_residuals/residualsX")
        residualsY_hist = add_histograms(file_list, f"AnalysisDUT/{plane}/global_residuals/residualsY")
        
        # 提取高斯拟合参数
        def fit_gaussian(hist):
            hist.Fit("gaus", "Q")
            fit = hist.GetFunction("gaus")
            mean = fit.GetParameter(1)
            sigma = fit.GetParameter(2)
            sigma_err = fit.GetParError(2)
            return sigma, sigma_err

        resx, resx_err = fit_gaussian(residualsX_hist)
        resy, resy_err = fit_gaussian(residualsY_hist)

        ret = {
            "eff_"      + plane + vcasb: add_histograms(file_list, f"AnalysisEfficiency/{plane}/eTotalEfficiency").GetEfficiency(1) * 100.0,
            "effl_"     + plane + vcasb: add_histograms(file_list, f"AnalysisEfficiency/{plane}/eTotalEfficiency").GetEfficiencyErrorLow(1) * 100.0,
            "effu_"     + plane + vcasb: add_histograms(file_list, f"AnalysisEfficiency/{plane}/eTotalEfficiency").GetEfficiencyErrorUp(1) * 100.0,
            "resx_"     + plane + vcasb: resx,
            "resx_err_" + plane + vcasb: resx_err,
            "resy_"     + plane + vcasb: resy,
            "resy_err_" + plane + vcasb: resy_err,
            "cs_"       + plane + vcasb: add_histograms(file_list, f"AnalysisDUT/{plane}/clusterSizeAssociated").GetMean(),
            "cs_err_"   + plane + vcasb: add_histograms(file_list, f"AnalysisDUT/{plane}/clusterSizeAssociated").GetMeanError()
        }
    except Exception as e:
        print(f"Error processing files {file_list}: {e}")  # QA语句：如果处理出错，输出错误信息
        ret = None
    return ret

#---------------------------------------------------------------------------------------
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('hfunit', choices=['t7', 't6', 'b4', 'bb', 'tb'])
    parser.add_argument('moss_name', choices=['MOSS-2_W02F4', 'MOSS-3_W08B6', 'babyMOSS-2_3_W04E2', 'babyMOSS-2_3_W24B5', 'babyMOSS-2_2_W21D4'])
    parser.add_argument(
        'directory', 
        type=str, 
        nargs='?', 
        default='/Users/wangchunzheng/works/moss_tool/analysis/output/', 
        help='Directory where the MOSS folders are located (default: /Users/wangchunzheng/works/moss_tool/analysis/output/)'
    )
    parser.add_argument('--no_add', action='store_true', help='If set, process only the first raw file without adding histograms')
    parser.add_argument('--highstat', '-hs', action='store_true', help='If set, use highstat directory structure')
    args = parser.parse_args()

    hfunit = args.hfunit
    moss_name = args.moss_name
    directory = args.directory
    no_add = args.no_add
    highstat = args.highstat
    decimals = 3

    # 如果moss_name开头是babyMOSS，那么hfunit只能是tb或者bb
    if moss_name.startswith('babyMOSS') and hfunit not in ['tb', 'bb']:
        print("Error: babyMOSS only has hfunit 'tb' or 'bb'.")
        exit(1)
    # 如果moss_name开头是MOSS，那么hfunit只能是t7, t6, b4
    if moss_name.startswith('MOSS') and hfunit not in ['t7', 't6', 'b4']:
        print("Error: MOSS only has hfunit 't7', 't6' or 'b4'.")
        exit(1)
    
    # 如果启用了 highstat，则修改正则表达式以支持带有 highstat 的目录
    if highstat:
        pattern = rf'{moss_name}_{hfunit}_region(\d+)_VCASB(\d+)_highstat'
    else:
        pattern = rf'{moss_name}_{hfunit}_region(\d+)_VCASB(\d+)'

    # Step 1: Extract all region and VCASB values and corresponding directories from the directory
    vcasb_dirs = {}
    folder_names = os.listdir(directory)
    
    print(f"Scanning directory: {directory}")  # QA语句：输出正在扫描的目录

    for folder in folder_names:
        match = re.search(pattern, folder)
        if match:
            region = int(match.group(1))
            vcasb_value = int(match.group(2))
            if region not in vcasb_dirs:
                vcasb_dirs[region] = {}
            vcasb_dirs[region][vcasb_value] = os.path.join(directory, folder)
    
    print(f"Found regions: {sorted(vcasb_dirs.keys())}")  # QA语句：输出找到的所有区域
    
    # Prepare the output structure
    output_json = {}

    # Sort regions and VCASB values before processing
    for region in sorted(vcasb_dirs.keys()):  # 按region顺序处理
        name = f"MOSS_reg{region}_3"
        x_axis = sorted(vcasb_dirs[region].keys())  # 按VCASB顺序处理

        region_data = {"VCASB": [], "eff": [], "eff_err_low": [], "eff_err_up": [], 
                       "res_RMS_mean": [], "res_err": [], 
                       "cluster_size_mean": [], "cluster_size_mean_err": []}

        for vcasb in x_axis:
            folder_path = vcasb_dirs[region][vcasb]
            root_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.root')]
            print(f"Region {region}, VCASB {vcasb}: Found {len(root_files)} ROOT files")  # QA语句：输出每个区域中找到的ROOT文件数量
            data = get_values_from_file(root_files, name, f'_{vcasb}', no_add)
            if data is None:
                print(f"No data processed for region {region}, VCASB {vcasb}. Skipping...")  # QA语句：输出处理失败的信息
                continue
            
            # Populate the data for each region
            region_data["VCASB"].append(vcasb)
            region_data["eff"].append(round(data[f"eff_{name}_{vcasb}"], decimals))
            region_data["eff_err_low"].append(round(data[f"effl_{name}_{vcasb}"], decimals))
            region_data["eff_err_up"].append(round(data[f"effu_{name}_{vcasb}"], decimals))
            region_data["res_RMS_mean"].append(round(data[f"resx_{name}_{vcasb}"], decimals))
            region_data["res_err"].append(round(data[f"resx_err_{name}_{vcasb}"], decimals))
            region_data["cluster_size_mean"].append(round(data[f"cs_{name}_{vcasb}"], decimals))
            region_data["cluster_size_mean_err"].append(round(data[f"cs_err_{name}_{vcasb}"], decimals))

        output_json[f"{region}"] = region_data  # 将每个 region 的数据放入对应的键中
    
    # 创建目标目录
    output_directory = os.path.join('json_files', moss_name, hfunit)
    os.makedirs(output_directory, exist_ok=True)
    print(f"Saving JSON output to: {output_directory}")  # QA语句：输出JSON文件保存路径

    # 保存 JSON 文件
    output_filepath = os.path.join(output_directory, f'{moss_name}_{hfunit}_eff.json')
    with open(output_filepath, 'w') as f:
        json.dump(output_json, f, indent=4)
    
    print(f"JSON file {output_filepath} has been created successfully!")  # QA语句：输出成功保存JSON文件的提示

#---------------------------------------------------------------------------------------