#!/bin/bash

case "$1" in
"b4")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=../../data/2023-08_PS/vcasb_scan_b4/run336114536_230820014850.raw"
    SIDE="bot"
    ;;
"b5")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=../../data/2023-08_PS/vcasb_scan_b5/run341144849_230822031608.raw"
    SIDE="bot"
    ;;
"t6")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=../../data/2023-08_PS/vcasb_scan_t6/run334162761_230818155257.raw"
    SIDE="top"
    ;;
"t7")
    OPT_FNAME="-o EventLoaderEUDAQ2.file_name=../../data/2023-08_PS/vcasb_scan_t7/run335203053_230819032602.raw"
    SIDE="top"
    ;;
*)
    echo "Unrecognised chip name $1"
    exit 1
    ;;
esac

SUFFIX=$1

corry -c configs/2023-08_PS/createmask.conf $OPT_FNAME -o MaskCreator.new_config_suffix=_${SUFFIX} -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SIDE}.conf -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_masked.conf -o histogram_file=${SUFFIX}_maskcreation.root

corry -c configs/2023-08_PS/prealign.conf $OPT_FNAME -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_masked.conf -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_prealigned.conf -o histogram_file=${SUFFIX}_prealignment.root

corry -c configs/2023-08_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=passive -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_prealigned.conf     -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf  -o histogram_file=${SUFFIX}_alignment_alpide.root
corry -c configs/2023-08_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=dut     -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=passive -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg0.conf    -o histogram_file=${SUFFIX}_alignment_reg0.root
corry -c configs/2023-08_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=dut     -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=passive -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg1.conf    -o histogram_file=${SUFFIX}_alignment_reg1.root
corry -c configs/2023-08_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=dut     -g MOSS_reg3_3.role=passive -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg2.conf    -o histogram_file=${SUFFIX}_alignment_reg2.root
corry -c configs/2023-08_PS/align.conf $OPT_FNAME -g MOSS_reg0_3.role=passive -g MOSS_reg1_3.role=passive -g MOSS_reg2_3.role=passive -g MOSS_reg3_3.role=dut     -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_alpide.conf -o detectors_file_updated=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg3.conf    -o histogram_file=${SUFFIX}_alignment_reg3.root

corry -c configs/2023-08_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=dut       -g MOSS_reg1_3.role=auxiliary -g MOSS_reg2_3.role=auxiliary -g MOSS_reg3_3.role=auxiliary  -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg0.conf -o histogram_file=${SUFFIX}_analysis_reg0.root
corry -c configs/2023-08_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=auxiliary -g MOSS_reg1_3.role=dut       -g MOSS_reg2_3.role=auxiliary -g MOSS_reg3_3.role=auxiliary  -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg1.conf -o histogram_file=${SUFFIX}_analysis_reg1.root
corry -c configs/2023-08_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=auxiliary -g MOSS_reg1_3.role=auxiliary -g MOSS_reg2_3.role=dut       -g MOSS_reg3_3.role=auxiliary  -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg2.conf -o histogram_file=${SUFFIX}_analysis_reg2.root
corry -c configs/2023-08_PS/analyse.conf $OPT_FNAME -g MOSS_reg0_3.role=auxiliary -g MOSS_reg1_3.role=auxiliary -g MOSS_reg2_3.role=auxiliary -g MOSS_reg3_3.role=dut        -o detectors_file=../../geometry/2023-08_PS_3REF-MOSS-3REF_${SUFFIX}_aligned_reg3.conf -o histogram_file=${SUFFIX}_analysis_reg3.root
