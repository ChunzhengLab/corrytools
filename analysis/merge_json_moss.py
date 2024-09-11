import json
import os
import sys

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def merge_data(data_list):
    merged_data = {}
    regions = data_list[0].keys()
    
    for region in regions:
        # Initialize the merged data structure with VCASB from the first dataset
        merged_data[region] = {
            "VCASB": data_list[0][region]["VCASB"]
        }
        
        # Iterate over each dataset to merge available keys dynamically
        for data in data_list:
            for key, value in data[region].items():
                if key == "VCASB":
                    continue  # Skip VCASB since it's already handled
                
                if key not in merged_data[region]:
                    merged_data[region][key] = [None] * len(merged_data[region]["VCASB"])  # Initialize with None

                # Create a mapping from VCASB values to their respective key values
                vcasb_value_map = dict(zip(data[region]["VCASB"], value))
                
                # Ensure that each value is placed at the correct VCASB position
                for idx, vcasb_value in enumerate(merged_data[region]["VCASB"]):
                    if vcasb_value in vcasb_value_map:
                        merged_data[region][key][idx] = vcasb_value_map[vcasb_value]
        
    return merged_data

def save_json(data, output_path):
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)

def main(hfunit, moss_name):
    # Construct the file paths
    base_path = f"json_files/{moss_name}/{hfunit}"
    eff_file = os.path.join(base_path, f"{moss_name}_{hfunit}_eff.json")
    thr_file = os.path.join(base_path, f"{moss_name}_{hfunit}_thr.json")
    fhr_file = os.path.join(base_path, f"{moss_name}_{hfunit}_fhr.json")

    # Load the JSON files
    data1 = load_json(eff_file)
    data2 = load_json(fhr_file)
    data3 = load_json(thr_file)

    # Combine the data into a list
    data_list = [data1, data2, data3]

    # Merge data according to VCASB
    merged_data = merge_data(data_list)

    # Save the merged data
    output_file = os.path.join(base_path, f"{moss_name}_{hfunit}.json")
    save_json(merged_data, output_file)

    print(f"Data merged successfully and saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <hfunit> <moss_name>")
    else:
        hfunit = sys.argv[1]
        moss_name = sys.argv[2]
        main(hfunit, moss_name)