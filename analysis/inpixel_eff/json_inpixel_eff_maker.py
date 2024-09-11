import ROOT
import json
import os

def extract_total_efficiency_info(tefficiency):
    total_efficiency = tefficiency.GetEfficiency(1)
    error_low = tefficiency.GetEfficiencyErrorLow(1)
    error_up = tefficiency.GetEfficiencyErrorUp(1)
    
    print(f"Total Efficiency: {total_efficiency}")
    print(f"Error Low: {error_low}")
    print(f"Error Up: {error_up}")

    return {
        "total_efficiency": total_efficiency,
        "errorlow_total": error_low,
        "errorup_total": error_up
    }

def extract_tefficiency_info(tefficiency, total_eff_info):
    info = {
        "row": [],
        "column": [],
        "efficiency": [],
        "errorlow": [],
        "errorup": [],
        "total_efficiency": total_eff_info["total_efficiency"],
        "errorlow_total": total_eff_info["errorlow_total"],
        "errorup_total": total_eff_info["errorup_total"]
    }
    
    nX = tefficiency.GetTotalHistogram().GetNbinsX()
    nY = tefficiency.GetTotalHistogram().GetNbinsY()

    for j in range(1, nY + 1):
        for i in range(1, nX + 1):
            bin_index = tefficiency.GetTotalHistogram().GetBin(i, j)
            eff = tefficiency.GetEfficiency(bin_index)
            error_low = tefficiency.GetEfficiencyErrorLow(bin_index)
            error_up = tefficiency.GetEfficiencyErrorUp(bin_index)
            
            info["row"].append(i - 1)
            info["column"].append(j - 1)
            info["efficiency"].append(eff)
            info["errorlow"].append(error_low)
            info["errorup"].append(error_up)
            
            print(f"Bin (Column {j-1}, Row {i-1}): Efficiency={eff}, Error Low={error_low}, Error Up={error_up}")

    return info

def extract_tprofile2d_info(tprofile2d):
    info = {
        "row": [],
        "column": [],
        "clustersize": [],
        "errorlow": [],
        "errorup": []
    }

    nX = tprofile2d.GetNbinsX()
    nY = tprofile2d.GetNbinsY()

    for j in range(1, nY + 1):
        for i in range(1, nX + 1):
            bin_index = tprofile2d.GetBin(i, j)
            clustersize = tprofile2d.GetBinContent(bin_index)
            error_low = tprofile2d.GetBinErrorLow(bin_index)
            error_up = tprofile2d.GetBinErrorUp(bin_index)
            
            info["row"].append(i - 1)
            info["column"].append(j - 1)
            info["clustersize"].append(clustersize)
            info["errorlow"].append(error_low)
            info["errorup"].append(error_up)
            
            print(f"Bin (Column {j-1}, Row {i-1}): Cluster Size={clustersize}, Error Low={error_low}, Error Up={error_up}")

    return info

def process_file(root_filepath, output_directory):
    # 获取文件名和路径
    filename = os.path.basename(root_filepath)
    name, _ = os.path.splitext(filename)
    
    # 打开ROOT文件
    root_file = ROOT.TFile.Open(root_filepath)
    if not root_file or root_file.IsZombie():
        print(f"Warning: Could not open ROOT file: {root_filepath}")
        return
    
    print(f"Opened ROOT file: {root_filepath}")

    # 处理每个region [0, 1, 2, 3]
    regions = [0, 1, 2, 3]

    for region in regions:
        # 提取 eTotalEfficiency 对象
        eTotalEfficiency = root_file.Get(f"AnalysisEfficiency/MOSS_reg{region}_3/eTotalEfficiency")
        if eTotalEfficiency:
            print(f"Extracting eTotalEfficiency for region {region}...")
            total_eff_info = extract_total_efficiency_info(eTotalEfficiency)
        else:
            print(f"Warning: eTotalEfficiency object not found for region {region}")
            continue  # 如果没找到，跳过这个 region

        # 提取 TEfficiency 对象
        tefficiency = root_file.Get(f"AnalysisEfficiency/MOSS_reg{region}_3/pixelEfficiencyMap_trackPos")
        if tefficiency:
            print(f"Extracting TEfficiency data for region {region}...")
            tefficiency_info = extract_tefficiency_info(tefficiency, total_eff_info)

            # 保存TEfficiency数据到JSON文件，避免重复包含 region
            output_filename = f"{name}_efficiency.json"
            with open(os.path.join(output_directory, output_filename), "w") as teff_file:
                json.dump(tefficiency_info, teff_file, indent=4)
                print(f"TEfficiency data saved for region {region}")
        else:
            print(f"Warning: TEfficiency object not found for region {region}")
            continue

        # 提取 TProfile2D 对象
        tprofile2d = root_file.Get(f"AnalysisDUT/MOSS_reg{region}_3/clusterSize_trackPos_TProfile")
        if tprofile2d:
            print(f"Extracting TProfile2D data for region {region}...")
            tprofile2d_info = extract_tprofile2d_info(tprofile2d)

            # 保存 TProfile2D 数据到 JSON 文件
            output_filename = f"{name}_clustersize.json"
            with open(os.path.join(output_directory, output_filename), "w") as tprofile2d_file:
                json.dump(tprofile2d_info, tprofile2d_file, indent=4)
                print(f"TProfile2D data saved for region {region}")
        else:
            print(f"Warning: TProfile2D object not found for region {region}")

    # 关闭 ROOT 文件
    root_file.Close()
    print(f"Closed ROOT file: {root_filepath}")

def main():
    # 设定输入输出路径
    input_directory = "./highstat_output"
    output_directory = "./json_files_inpixel"
    os.makedirs(output_directory, exist_ok=True)
    
    # 遍历目录中的所有ROOT文件
    for filename in os.listdir(input_directory):
        if filename.endswith(".root"):
            root_filepath = os.path.join(input_directory, filename)
            process_file(root_filepath, output_directory)

if __name__ == "__main__":
    main()