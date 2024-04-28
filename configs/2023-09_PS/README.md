Each region of the MOSS sensor was treated as an independent DUT, ignoring other regions.
Alignment of the tracking planes and MOSS sensor was done simultaneously by requiring for a track reconstruction hits in all planes (in total, 7 hits).

The MOSS testbeam data analysis is based on the following config files and scripts:

1) **templates of geometry files for MOSS top and bottom units** (`/geometry/2023-09_PS_3REF-MOSS-3REF_bot.conf & /geometry/2023-09_PS_3REF-MOSS-3REF_top.conf`):

The script `make_geometry.sh` generates the geometry file for each MOSS region (0,1,2,3) based on a template file.
Keywords `NUM, X_COORDINATE, and MAT_BUDGET` are replaced by the appropriate values, which vary from region to region. 
All needed variables are defined in the `make_geometry.sh` script.

2) **config files to run Corry analysis**:

Parameters of modules with empty strings are provided externally to the Corryvrekan software.
Example of the Corry running command (`telescope alignment`) for the MOSS region 0, B4 unit:
`corry -c ../../align.conf -o detectors_file=../geometry/b4/MOSS_reg0/prealigned_b4.conf -o detectors_file_updated=../geometry/b4/MOSS_reg0/aligned_b4.conf -o histogram_file=alignment_b4.root -o output_directory=b4/MOSS_reg0 -o EventLoaderEUDAQ2.file_name=../data/vcasb_scan_b4/run394145838_230928224026.raw -o Tracking4D.require_detectors=ALPIDE_0,ALPIDE_1,ALPIDE_2,ALPIDE_4,ALPIDE_5,ALPIDE_6,MOSS_reg0_3`.
To generate the needed Corry commands (for `masking, prealignment, alignment, and analysis`), `make_scripts4run.sh` script is used.

**IMPORTANT:** The scripts are not versatile; If you want to use the scripts, then **you need to adapt them to your analysis**.