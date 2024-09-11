import os
from glob import glob
import argparse
import ROOT

def get_dir_names(moss_name, hfunit, region, base_dir=None):
    if base_dir is None:
        base_dir = "/Users/wangchunzheng/works/moss_tool/analysis/output"

    # 自动检测所有可能的 VCASB 后的值
    search_pattern = f"{moss_name}_{hfunit}_region{region}_VCASB*_highstat"
    possible_dirs = glob(os.path.join(base_dir, search_pattern))
    
    if not possible_dirs:
        print(f"Warning: No directory found matching pattern: {search_pattern}")
        return []

    print(f"Found directories: {possible_dirs}")
    return possible_dirs

def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it.")
        os.makedirs(directory)

def safe_add_histograms(h1, h2):
    try:
        if h1.GetNbinsX() != h2.GetNbinsX() or h1.GetNbinsY() != h2.GetNbinsY():
            print(f"Skipping incompatible histograms {h1.GetName()} and {h2.GetName()} due to different bin numbers or axis limits")
            return
        h1.Add(h2)
        print(f"Successfully merged histogram: {h1.GetName()}")
    except Exception as e:
        print(f"Error merging histograms {h1.GetName()} and {h2.GetName()}: {e}")

def process_directory(file, directory_path, objects_dict, target_objects, root_file):
    if not file.cd(directory_path):
        print(f"Directory {directory_path} not found in file {root_file}. Skipping.")
        return

    keys = ROOT.gDirectory.GetListOfKeys()
    for key in keys:
        obj_name = key.GetName()

        if obj_name not in target_objects:
            continue

        obj = key.ReadObj()

        if obj_name in objects_dict:
            if isinstance(obj, (ROOT.TH1, ROOT.TProfile, ROOT.TProfile2D, ROOT.TH2D, ROOT.TH2F)):
                safe_add_histograms(objects_dict[obj_name], obj)
            elif isinstance(obj, ROOT.TEfficiency):
                objects_dict[obj_name].append(obj.Clone())
            else:
                print(f"Skipping non-TH1/TProfile/TProfile2D/TH2D/TH2F/TEfficiency object: {obj_name} in file: {root_file}")
        else:
            if isinstance(obj, (ROOT.TH1, ROOT.TProfile, ROOT.TProfile2D, ROOT.TH2D, ROOT.TH2F)):
                objects_dict[obj_name] = obj.Clone()
                objects_dict[obj_name].SetDirectory(0)
            elif isinstance(obj, ROOT.TEfficiency):
                objects_dict[obj_name] = [obj.Clone()]
            else:
                print(f"Skipping non-TH1/TProfile/TProfile2D/TH2D/TH2F/TEfficiency object: {obj_name} in file: {root_file}")

def add_root_objects(input_dir, output_file, region):
    search_path = os.path.join(input_dir, 'analysis_VCASB*.root')
    print(f"Searching for ROOT files with pattern: {search_path}")
    
    root_files = glob(search_path)

    if len(root_files) == 0:
        print(f"Warning: No ROOT files found matching the pattern in the specified directory: {input_dir}")
        return

    ensure_dir_exists(os.path.dirname(output_file))

    output_root = ROOT.TFile(output_file, 'RECREATE')
    efficiency_objects = {}
    dut_objects = {}

    target_objects = [
        "clusterSize_trackPos_TProfile",
        "eTotalEfficiency",
        "efficiencyColumns",
        "efficiencyRows",
        "pixelEfficiencyMap_trackPos",
        "pixelEfficiencyMap_trackPos_TProfile"
    ]

    for root_file in root_files:
        print(f"Processing file: {root_file}")
        file = ROOT.TFile(root_file, 'READ')
        
        process_directory(file, f'AnalysisEfficiency/MOSS_reg{region}_3', efficiency_objects, target_objects, root_file)
        process_directory(file, f'AnalysisDUT/MOSS_reg{region}_3', dut_objects, target_objects, root_file)

        file.Close()

    def merge_efficiency_objects(objects_dict):
        for obj_name, obj_list in objects_dict.items():
            if isinstance(obj_list, list) and isinstance(obj_list[0], ROOT.TEfficiency):
                merged_obj = obj_list[0].Clone()
                merge_list = ROOT.TList()
                for obj in obj_list[1:]:
                    merge_list.Add(obj)
                merged_obj.Merge(merge_list)
                objects_dict[obj_name] = merged_obj

    merge_efficiency_objects(efficiency_objects)
    merge_efficiency_objects(dut_objects)

    def save_objects_to_directory(objects_dict, base_directory_name, region):
        for obj_name, obj in objects_dict.items():
            directory_name = f"{base_directory_name}/MOSS_reg{region}_3"
            output_root.mkdir(directory_name)
            output_root.cd(directory_name)
            try:
                if isinstance(obj, list):
                    obj[0].Write()
                else:
                    obj.Write()
                print(f"Successfully saved object: {obj.GetName()} in {directory_name}")
            except Exception as e:
                print(f"Error writing object {obj.GetName()}: {e}")

    save_objects_to_directory(efficiency_objects, 'AnalysisEfficiency', region)
    save_objects_to_directory(dut_objects, 'AnalysisDUT', region)

    output_root.Close()
    print(f"All specified objects have been summed and saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sum specified ROOT objects from multiple files.")
    parser.add_argument('moss_name', choices=['MOSS-2_W02F4', 'MOSS-3_W08B6', 'babyMOSS-2_3_W04E2', 'babyMOSS-2_3_W24B5', 'babyMOSS-2_2_W21D4'], help='MOSS Name (e.g., MOSS-2_W02F4, babyMOSS-2_3_W04E2)')
    parser.add_argument('hfunit', choices=['t7', 't6', 'b4', 'tb', 'bb'], help='HFUnit (e.g., t7, t6, b4, tb, bb)')
    parser.add_argument('--output_dir', default='./highstat_output', help='Output directory for the summed ROOT file')
    args = parser.parse_args()

    for region in range(4):  # 自动检测 0-3 区域
        input_directories = get_dir_names(args.moss_name, args.hfunit, region)
        if not input_directories:
            continue
        
        for input_directory in input_directories:
            # 从路径中提取 VCASB 值
            vcasb_value = input_directory.split("_VCASB")[1].split("_")[0]
            
            output_dir = args.output_dir
            output_file = f"{args.moss_name}_{args.hfunit}_region{region}_VCASB{vcasb_value}_highstat.root"
            output_file = os.path.join(output_dir, output_file)
            add_root_objects(input_directory, output_file, region)