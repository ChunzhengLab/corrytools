#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import shutil
import time

def main():
    # Initialize default variables
    SKIP_MASK = False
    HIGHSTAT = False
    ONLY_ANALYSE = False

    # Set experiment period
    TB_PERIOD = "2024-08_PS_II"
    # Set default data directory path and config file path prefix
    GEOMETRY_DIR = "/local/geometry"
    GEOMETRY_UPDATE_DIR = "/local/analysis/geometry_update"
    CONFIG_DIR_BASE = "/local/configs"
    CONFIG_DIR = os.path.join(CONFIG_DIR_BASE, TB_PERIOD)

    # Valid MOSS names and HFUnits
    VALID_MOSS_NAMES = [
        "babyMOSS-2_2_W21D4",
        "MOSS-3_W08B6",
        "MOSS-2_W02F4",
        "babyMOSS-2_3_W04E2",
        "babyMOSS-2_3_W24B5"
    ]

    VALID_HFUNITS_BABYMOSS = ["bb", "tb"]
    VALID_HFUNITS_MOSS = ["t" + str(i) for i in range(100)] + ["b" + str(i) for i in range(100)]  # Adjust range as needed

    parser = argparse.ArgumentParser(description="Process and analyze MOSS data.")
    parser.add_argument("--skip-mask", action="store_true", help="Skip applying the mask.")
    parser.add_argument("--high-stat", action="store_true", help="Use high-statistics data.")
    parser.add_argument("--only-analyse", action="store_true", help="Only run analysis, skip alignment steps.")
    parser.add_argument("--region", type=str, help="Comma-separated list of regions to process (0,1,2,3).")
    parser.add_argument("MOSS", type=str, help="MOSS name. Valid options: {}".format(", ".join(VALID_MOSS_NAMES)))
    parser.add_argument("HFUnit", type=str, help="HFUnit. For babyMOSS: bb or tb. For MOSS: tN or bN, where N is a number.")
    args = parser.parse_args()

    # Assign parsed arguments to variables
    SKIP_MASK = args.skip_mask
    HIGHSTAT = args.high_stat
    ONLY_ANALYSE = args.only_analyse
    MOSS = args.MOSS
    HFUnit = args.HFUnit

    # Validate MOSS and HFUnit
    if MOSS not in VALID_MOSS_NAMES:
        print("Error: Invalid MOSS name provided.")
        sys.exit(1)

    if MOSS.startswith("babyMOSS"):
        if HFUnit not in VALID_HFUNITS_BABYMOSS:
            print("Error: For babyMOSS, HFUnit must be 'bb' or 'tb'.")
            sys.exit(1)
    elif MOSS.startswith("MOSS"):
        if not (HFUnit.startswith('t') or HFUnit.startswith('b')) or not HFUnit[1:].isdigit():
            print("Error: For MOSS, HFUnit must be 'tN' or 'bN' (where N is a number).")
            sys.exit(1)
    else:
        print("Error: Invalid MOSS name provided.")
        sys.exit(1)

    # Determine regions to process
    if args.region:
        regions = args.region.split(',')
        REGIONS = [int(r.strip()) for r in regions if r.strip().isdigit()]
        invalid_regions = [r for r in REGIONS if r not in [0,1,2,3]]
        if invalid_regions:
            print("Error: Invalid region(s) specified: {}".format(", ".join(map(str, invalid_regions))))
            sys.exit(1)
    else:
        # If no regions specified, default to all regions
        REGIONS = [0,1,2,3]

    # Based on MOSS and HFUnit, set geometry configuration file
    if MOSS.startswith("babyMOSS"):
        if HFUnit == "tb":
            GEOMETRY_FILE = os.path.join(GEOMETRY_DIR, "{}_3REF-MOSS-3REF_tb.conf".format(TB_PERIOD))
        elif HFUnit == "bb":
            GEOMETRY_FILE = os.path.join(GEOMETRY_DIR, "{}_3REF-MOSS-3REF_bb.conf".format(TB_PERIOD))
    elif MOSS.startswith("MOSS"):
        if HFUnit.startswith("t"):
            GEOMETRY_FILE = os.path.join(GEOMETRY_DIR, "{}_3REF-MOSS-3REF_top.conf".format(TB_PERIOD))
        elif HFUnit.startswith("b"):
            GEOMETRY_FILE = os.path.join(GEOMETRY_DIR, "{}_3REF-MOSS-3REF_bottom.conf".format(TB_PERIOD))

    print("Using geometry file: {}".format(GEOMETRY_FILE))
    print("Using config directory: {}".format(CONFIG_DIR))

    # Ensure the update directory exists
    os.makedirs(GEOMETRY_UPDATE_DIR, exist_ok=True)

    # Record the start time of the script
    START_TOTAL = time.time()

    # Create dictionaries to store mask files and minimum VCASB for each region
    MASK_FILES = {}
    MIN_VCASB = {}

    # Process each region
    for REGION in REGIONS:
        # Set DATA_DIR based on HIGHSTAT flag
        if HIGHSTAT:
            DATA_DIR = "/local/data/{}/{}/{}_psub12_highstat/region{}".format(TB_PERIOD, MOSS, HFUnit, REGION)
        else:
            DATA_DIR = "/local/data/{}/{}/{}_psub12/region{}".format(TB_PERIOD, MOSS, HFUnit, REGION)

        # Find the minimum VCASB directory
        vcasb_dirs = []
        if os.path.isdir(DATA_DIR):
            for d in os.listdir(DATA_DIR):
                if d.startswith("VCASB") and os.path.isdir(os.path.join(DATA_DIR, d)):
                    vcasb_dirs.append(d)
        if not vcasb_dirs:
            print("Warning: No VCASB directories found for Region {}. Skipping this region.".format(REGION))
            continue

        # Sort VCASB directories and pick the minimum
        vcasb_dirs.sort()
        min_vcasb_dir = os.path.join(DATA_DIR, vcasb_dirs[0])

        # Check for .raw files in the minimum VCASB directory
        raw_files = [f for f in os.listdir(min_vcasb_dir) if f.endswith(".raw") and os.path.isfile(os.path.join(min_vcasb_dir, f))]
        if not raw_files:
            print("Warning: No .raw files found for Region {}. Skipping this region.".format(REGION))
            continue

        min_vcasb = os.path.basename(min_vcasb_dir)
        MIN_VCASB[REGION] = min_vcasb

        # Generate the target geometry update file name
        if HIGHSTAT:
            GEOMETRY_UPDATE_FILE = os.path.join(GEOMETRY_UPDATE_DIR,
                "{}_3REF-MOSS-3REF_{}_{}_region{}_{}_highstat_masked.conf".format(TB_PERIOD, MOSS, HFUnit, REGION, min_vcasb))
        else:
            GEOMETRY_UPDATE_FILE = os.path.join(GEOMETRY_UPDATE_DIR,
                "{}_3REF-MOSS-3REF_{}_{}_region{}_{}_masked.conf".format(TB_PERIOD, MOSS, HFUnit, REGION, min_vcasb))

        # Create the updated geometry configuration file
        if not ONLY_ANALYSE:
            shutil.copy(GEOMETRY_FILE, GEOMETRY_UPDATE_FILE)

            # If SKIP_MASK is False, add mask_file line
            if not SKIP_MASK:
                MASK_FILE_PATH = 'mask_files/masked_pixel_{}_{}_reg{}.txt'.format(MOSS, HFUnit, REGION)
                # Add the mask_file line to the configuration file
                with open(GEOMETRY_UPDATE_FILE, 'a') as f:
                    f.write('\n[MOSS_reg{}_3]\nmask_file = "{}"\n'.format(REGION, MASK_FILE_PATH))

            MASK_FILES[REGION] = GEOMETRY_UPDATE_FILE
            print("Created geometry file with mask: {}".format(GEOMETRY_UPDATE_FILE))

    # Process alignment and analysis for each region
    for REGION in REGIONS:
        min_vcasb = MIN_VCASB.get(REGION)
        if not min_vcasb:
            print("Skipping Region {} as no minimum VCASB was found.".format(REGION))
            continue

        # Set DATA_DIR based on HIGHSTAT flag
        if HIGHSTAT:
            DATA_DIR = "/local/data/{}/{}/{}_psub12_highstat/region{}".format(TB_PERIOD, MOSS, HFUnit, REGION)
        else:
            DATA_DIR = "/local/data/{}/{}/{}_psub12/region{}".format(TB_PERIOD, MOSS, HFUnit, REGION)

        min_vcasb_dir = os.path.join(DATA_DIR, min_vcasb)

        # Find the largest numbered .raw file in the minimum VCASB directory
        raw_files = [f for f in os.listdir(min_vcasb_dir) if f.endswith(".raw")]
        if not raw_files:
            print("Warning: No .raw file found in {}, skipping Region {}.".format(min_vcasb_dir, REGION))
            continue
        raw_files.sort()
        min_raw_file = os.path.join(min_vcasb_dir, raw_files[-1])

        print("Region {}: min_vcasb_dir = {}".format(REGION, min_vcasb_dir))
        print("Region {}: min_raw_file = {}".format(REGION, min_raw_file))

        SUFFIX_MIN = "{}_{}_region{}_{}".format(MOSS, HFUnit, REGION, min_vcasb)
        OPT_FNAME_MIN = "-o EventLoaderEUDAQ2.file_name={}".format(min_raw_file)

        if HIGHSTAT:
            OUTPUT_DIR_MIN = "/local/analysis/output/{}_highstat".format(SUFFIX_MIN)
        else:
            OUTPUT_DIR_MIN = "/local/analysis/output/{}".format(SUFFIX_MIN)
        os.makedirs(OUTPUT_DIR_MIN, exist_ok=True)

        DETECTORS_FILE = os.path.join(GEOMETRY_UPDATE_DIR, "{}_3REF-MOSS-3REF_{}_aligned.conf".format(TB_PERIOD, SUFFIX_MIN))

        print("ONLY_ANALYSE: {}".format(ONLY_ANALYSE))
        print("DETECTORS_FILE: {}".format(DETECTORS_FILE))
        print("DETECTORS_FILE exists: {}".format("yes" if os.path.isfile(DETECTORS_FILE) else "no"))

        if ONLY_ANALYSE and os.path.isfile(DETECTORS_FILE):
            print("Skipping alignment for Region {} since detectors_file exists: {}".format(REGION, DETECTORS_FILE))
        else:
            print("Proceeding with alignment for Region {}".format(REGION))

            # Execute prealign step
            prealign_command = [
                'corry', '-c', os.path.join(CONFIG_DIR, 'prealign.conf'), OPT_FNAME_MIN,
                '-o', 'detectors_file={}'.format(MASK_FILES[REGION]),
                '-o', 'detectors_file_updated={}'.format(
                    os.path.join(GEOMETRY_UPDATE_DIR, "{}_3REF-MOSS-3REF_{}_prealigned.conf".format(TB_PERIOD, SUFFIX_MIN))),
                '-o', 'histogram_file=prealignment.root',
                '-o', 'output_directory={}'.format(OUTPUT_DIR_MIN)
            ]
            result = subprocess.run(' '.join(prealign_command), shell=True)
            if result.returncode != 0:
                print("Prealign step failed for Region {}".format(REGION))
                sys.exit(1)

            # Execute alignment steps
            # First alignment
            align_command_1 = [
                'corry', '-c', os.path.join(CONFIG_DIR, 'align.conf'), OPT_FNAME_MIN,
                '-g', 'MOSS_reg0_3.role=passive',
                '-g', 'MOSS_reg1_3.role=passive',
                '-g', 'MOSS_reg2_3.role=passive',
                '-g', 'MOSS_reg3_3.role=passive',
                '-o', 'detectors_file={}'.format(os.path.join(
                    GEOMETRY_UPDATE_DIR, "{}_3REF-MOSS-3REF_{}_prealigned.conf".format(TB_PERIOD, SUFFIX_MIN))),
                '-o', 'detectors_file_updated={}'.format(os.path.join(
                    GEOMETRY_UPDATE_DIR, "{}_3REF-MOSS-3REF_{}_refaligned.conf".format(TB_PERIOD, SUFFIX_MIN))),
                '-o', 'histogram_file=refalignment.root',
                '-o', 'output_directory={}'.format(OUTPUT_DIR_MIN)
            ]
            result = subprocess.run(' '.join(align_command_1), shell=True)
            if result.returncode != 0:
                print("Alignment step failed for Region {}".format(REGION))
                sys.exit(1)

            # Second alignment
            role_options = []
            for r in [0,1,2,3]:
                role = "dut" if r == REGION else "auxiliary"
                role_options.extend(['-g', 'MOSS_reg{}_3.role={}'.format(r, role)])
            align_command_2 = [
                'corry', '-c', os.path.join(CONFIG_DIR, 'align.conf'), OPT_FNAME_MIN
            ] + role_options + [
                '-o', 'detectors_file={}'.format(os.path.join(
                    GEOMETRY_UPDATE_DIR, "{}_3REF-MOSS-3REF_{}_refaligned.conf".format(TB_PERIOD, SUFFIX_MIN))),
                '-o', 'detectors_file_updated={}'.format(DETECTORS_FILE),
                '-o', 'histogram_file=alignment.root',
                '-o', 'output_directory={}'.format(OUTPUT_DIR_MIN)
            ]
            result = subprocess.run(' '.join(align_command_2), shell=True)
            if result.returncode != 0:
                print("Final alignment step failed for Region {}".format(REGION))
                sys.exit(1)

        # Analysis step
        # For each VCASB directory
        vcasb_dirs = [d for d in os.listdir(DATA_DIR) if d.startswith("VCASB") and os.path.isdir(os.path.join(DATA_DIR, d))]
        for dir_name in vcasb_dirs:
            dir_path = os.path.join(DATA_DIR, dir_name)
            # Find all .raw files
            raw_files = [f for f in os.listdir(dir_path) if f.endswith(".raw")]
            if not raw_files:
                print("No .raw files found in {}, skipping.".format(dir_path))
                continue

            # Initialize file counter
            file_counter = 0

            for raw_file in raw_files:
                VCASB = dir_name
                if HIGHSTAT:
                    SUFFIX = "{}_{}_region{}_{}_highstat".format(MOSS, HFUnit, REGION, VCASB)
                else:
                    SUFFIX = "{}_{}_region{}_{}".format(MOSS, HFUnit, REGION, VCASB)

                OPT_FNAME = "-o EventLoaderEUDAQ2.file_name={}".format(os.path.join(dir_path, raw_file))
                OUTPUT_DIR = "/local/analysis/output/{}".format(SUFFIX)
                os.makedirs(OUTPUT_DIR, exist_ok=True)

                START = time.time()

                # Set inpixel_bin_size based on HFUnit
                if HFUnit == "tb":
                    BIN_SIZE_OPTION = "-o AnalysisDUT.inpixel_bin_size=2.5um -o AnalysisEfficiency.inpixel_bin_size=2.5um"
                elif HFUnit == "bb":
                    BIN_SIZE_OPTION = "-o AnalysisDUT.inpixel_bin_size=2.0um -o AnalysisEfficiency.inpixel_bin_size=2.0um"
                else:
                    BIN_SIZE_OPTION = ""

                role_options = []
                for r in [0,1,2,3]:
                    role = "dut" if r == REGION else "auxiliary"
                    role_options.extend(['-g', 'MOSS_reg{}_3.role={}'.format(r, role)])

                analysis_command = [
                    'corry', '-c', os.path.join(CONFIG_DIR, 'analyse.conf'), OPT_FNAME
                ] + role_options + [
                    '-o', 'detectors_file={}'.format(DETECTORS_FILE),
                    '-o', 'histogram_file=analysis_{}_{}.root'.format(VCASB, file_counter),
                    '-o', 'output_directory={}'.format(OUTPUT_DIR),
                    '-l', os.path.join(OUTPUT_DIR, 'analysis_{}_{}.log'.format(VCASB, file_counter)),
                    BIN_SIZE_OPTION
                ]
                result = subprocess.run(' '.join(analysis_command), shell=True)
                END = time.time()
                DIFF = END - START
                print("Analysis for {} in Region {} completed in {} seconds.".format(raw_file, REGION, int(DIFF)))
                file_counter +=1

    # Record the end time of the script
    END_TOTAL = time.time()
    DIFF_TOTAL = END_TOTAL - START_TOTAL
    print("Total time for the script: {} seconds.".format(int(DIFF_TOTAL)))

if __name__ == "__main__":
    main()