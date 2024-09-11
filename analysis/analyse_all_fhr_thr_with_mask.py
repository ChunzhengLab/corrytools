import argparse
import os
import subprocess

def find_files(directory, name, exclude_pattern=None, absolute_path=False):
    """Implementation of the terminal command 'find' to search for files with the given name, in the given directory. Use '*' for wildcard.

    Args:
        directory (str): Directory to start the search.
        name (str): The file name to search for. Pass a list of strings to look for several patterns.
        exclude_pattern (str, optional): Pattern to exclude from the search. Pass a list of strings to exclude several patterns. Defaults to None.
        absolute_path (bool, optional): Return the absolute path of the files found. Defaults to False.

    Returns:
        list: A list of strings with relative path to the files that match the file name.
    """
    command = []
    if directory[0] == '~': 
        directory = os.path.expanduser(directory)
    if type(name) is not list: 
        name = [name] 
    if type(exclude_pattern) is not list: 
        exclude_pattern = [exclude_pattern]

    def add_exclude_pattern():
        for _exclude_pattern in exclude_pattern:
            command.extend(["-not", "-path", _exclude_pattern])

    command = ["find", directory]
    command.extend(["-name", name[0]])
    if exclude_pattern[0]: 
        add_exclude_pattern()
    if not absolute_path: 
        command.extend(["-printf", "%P\n"])

    for _name in name[1:]:
        command.extend(["-o", "-name", _name])
        if exclude_pattern[0]: 
            add_exclude_pattern()
        if not absolute_path: 
            command.extend(["-printf", "%P\n"])
    result = subprocess.run(command, capture_output=True, text=True)
    result = result.stdout.splitlines()
    return result

def _load_folders(data_dir):
    paths = find_files(directory=data_dir, name='scan_result.json*', absolute_path=True)
    folders = [os.path.dirname(path) for path in paths]
    return folders

def _remove_analysed_scans(folders):
    return [folder for folder in folders if not find_files(directory=folder, name='analysis_result.json*', absolute_path=True)]

def _remove_failed_scans(folders):
    ret_list = []
    for folder in folders:
        scan_results_path = os.path.join(folder, 'scan_result.json')
        try:
            with open(scan_results_path, 'r') as file:
                if any('"scan_result": "OK"' in line or "'scan_result': 'OK'" in line for line in file):
                    ret_list.append(folder)
        except FileNotFoundError:
            pass
    return ret_list

def _separate_folders(folders):
    thr_list, fhr_list = [], []
    for folder in folders:
        tb_log_path = os.path.join(folder, "log", "tb.log")
        try:
            with open(tb_log_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if 'ThresholdScan' in line:
                        thr_list.append(folder)
                        break                
                    if 'FakeHitRateScan' in line:
                        fhr_list.append(folder)
                        break
        except FileNotFoundError:
            pass
    return thr_list, fhr_list

def _create_folder_list(data_dir, re_analyse=False):
    folders = _load_folders(data_dir)
    if not re_analyse:
        folders = _remove_analysed_scans(folders)
    folders = _remove_failed_scans(folders)
    thr_list, fhr_list = _separate_folders(folders)
    return thr_list, fhr_list

def _analyse_thr(thr_list, sw_analyse_dir):
    for thr in thr_list:
        command = f'{sw_analyse_dir}/thr_scan_analysis.py {thr} -q'
        os.system(command)

def _analyse_fhr(fhr_list, sw_analyse_dir, fm, mask_file):
    for fhr in fhr_list:
        command = f'{sw_analyse_dir}/fhr_analysis.py {fhr} -q'
        if fm:
            command += ' -fm'
        if mask_file:
            command += f' -m {mask_file}'
        os.system(command)

def analyse_all(data_dir, sw_analyse_dir, only_thr=False, only_fhr=False, re_analyse=False, fm=False, mask_file=None):
    thr_list, fhr_list = _create_folder_list(data_dir, re_analyse)
    if not only_fhr and not only_thr:
        only_fhr = only_thr = True
    if only_thr:
        _analyse_thr(thr_list, sw_analyse_dir)
    if only_fhr:
        _analyse_fhr(fhr_list, sw_analyse_dir, fm, mask_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search recursively through a directory and analyse all data sets that are not yet analysed.")
    parser.add_argument('DATA_DIRECTORY', nargs='*', default=['/home/palpidefs/MOSS_TEST_RESULTS'], help="Any number of directories to search through.")
    parser.add_argument('--only_thr', '-thr', action='store_true', help="Only analyse Thereshold Scans.")
    parser.add_argument('--only_fhr', '-fhr', action='store_true', help="Only analyse FakeHitRate Scans.")
    parser.add_argument('--re_analyse', '-a', action='store_true', help="Rerun analysis of already analysed files.")
    parser.add_argument('--fm', "-fm", action='store_true', help="Add the '-fm' flag to fhr_analysis.py command.")
    parser.add_argument('--m', "-m", type=str, help="Specify a mask file for the '-m' flag in fhr_analysis.py command.")
    
    args = parser.parse_args()

    data_dirs = args.DATA_DIRECTORY
    re_analyse = args.re_analyse
    sw_analyse_dir = '/opt/sw/analyses'
    only_thr = args.only_thr
    only_fhr = args.only_fhr
    fm = args.fm
    mask_file = args.m

    for data_dir in data_dirs:
        analyse_all(data_dir, sw_analyse_dir, only_thr, only_fhr, re_analyse, fm, mask_file)