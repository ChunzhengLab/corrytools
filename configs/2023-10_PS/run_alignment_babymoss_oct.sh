#!/bin/bash

SIDE="top"
case "$1" in
"t5_wo_psub")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run434003413_231026053920.raw"
    ;;
"t5_psub0")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run437001532_231029023839.raw"
    ;;
"t5_psub03")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run434185747_231026213102.raw"
    ;;
"t5_psub06")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run435171831_231027193000.raw"
    ;;
"t5_psub09")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run435171842_231028050656.raw"
    ;;
"t5_psub12")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run435171854_231028153009.raw"
    ;;
"t5_psub15")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=/../../run437001544_231029132001.raw"
    ;;
*)
    echo "Unrecognised chip name $1"
    exit 1
    ;;
esac



SUFFIX=$1

corry -c configs/2023-10_PS/createmask.conf $OPT_FNAME -o MaskCreator.new_config_suffix=_${SUFFIX} -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SIDE}.conf -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_masked.conf -o histogram_file=${SUFFIX}_maskcreation.root

corry -c configs/2023-10_PS/prealign.conf $OPT_FNAME -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_masked.conf -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_prealigned.conf -o histogram_file=${SUFFIX}_prealignment.root

corry -c configs/2023-10_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=passive -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_prealigned.conf     -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf  -o histogram_file=${SUFFIX}_alignment_alpide.root

corry -c configs/2023-10_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=dut     -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=passive -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg0.conf    -o histogram_file=${SUFFIX}_alignment_reg0.root
corry -c configs/2023-10_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=dut     -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=passive -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg1.conf    -o histogram_file=${SUFFIX}_alignment_reg1.root
corry -c configs/2023-10_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=dut     -g MOSS_reg3_3.role=passive -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg2.conf    -o histogram_file=${SUFFIX}_alignment_reg2.root
corry -c configs/2023-10_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=dut     -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg3.conf    -o histogram_file=${SUFFIX}_alignment_reg3.root

corry -c configs/2023-10_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=dut       -g MOSS_reg1_3.role=auxiliary -g MOSS_reg2_3.role=auxiliary -g MOSS_reg3_3.role=auxiliary  -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg0.conf -o histogram_file=${SUFFIX}_analysis_reg0.root
corry -c configs/2023-10_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=auxiliary -g MOSS_reg1_3.role=dut       -g MOSS_reg2_3.role=auxiliary -g MOSS_reg3_3.role=auxiliary  -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg1.conf -o histogram_file=${SUFFIX}_analysis_reg1.root
corry -c configs/2023-10_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=auxiliary -g MOSS_reg1_3.role=auxiliary -g MOSS_reg2_3.role=dut       -g MOSS_reg3_3.role=auxiliary  -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg2.conf -o histogram_file=${SUFFIX}_analysis_reg2.root
corry -c configs/2023-10_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=auxiliary -g MOSS_reg1_3.role=auxiliary -g MOSS_reg2_3.role=auxiliary -g MOSS_reg3_3.role=dut        -o detectors_file=/../../2023-10_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg3.conf -o histogram_file=${SUFFIX}_analysis_reg3.root

