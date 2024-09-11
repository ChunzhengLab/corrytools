#!/bin/bash

# 初始化标志变量
SKIP_MASK=false
# 设置实验周期
TB_PERIOD="2024-08_PS_II"
# 设置默认的数据目录路径和配置文件路径前缀
GEOMETRY_DIR="/local/geometry"
GEOMETRY_UPDATE_DIR="/local/analysis/geometry_update"
CONFIG_DIR_BASE="/local/configs"
CONFIG_DIR="${CONFIG_DIR_BASE}/${TB_PERIOD}"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-mask)
            SKIP_MASK=true
            shift
            ;;
        MOSS-3_W08B6 | MOSS-2_W02F4 | babyMOSS-2_3_W04E2 | babyMOSS-2_3_W24B5 | babyMOSS-2_2_W21D4)
            MOSS=$1
            shift
            ;;
        t[0-9]* | b[0-9]* | bb | tb)
            HFUnit=$1
            shift
            ;;
        *)
            echo "Usage: $0 [--skip-mask] <MOSS-3_W08B6 or MOSS-2_W02F4 or babyMOSS-2_3_W04E2> <tN or nN or bb or tb>"
            exit 1
            ;;
    esac
done

# 检查必要的参数是否提供
if [ -z "$MOSS" ] || [ -z "$HFUnit" ]; then
    echo "Error: MOSS name and HFUnit must be provided."
    echo "Usage: $0 [--skip-mask] <MOSS-3_W08B6 or MOSS-2_W02F4 or babyMOSS-2_3_W04E2> <tN or nN or bb or tb>"
    exit 1
fi

# 检查 MOSS 和 HFUnit 的组合是否有效
if [[ $MOSS == babyMOSS-* ]]; then
    if [[ $HFUnit != "bb" && $HFUnit != "tb" ]]; then
        echo "Error: For babyMOSS, HFUnit must be 'bb' or 'tb'."
        exit 1
    fi
elif [[ $MOSS == MOSS-* ]]; then
    if [[ ! $HFUnit =~ ^(t[0-9]+|b[0-9]+)$ ]]; then
        echo "Error: For MOSS, HFUnit must be 'tN' or 'nN' (where N is a number)."
        exit 1
    fi
else
    echo "Error: Invalid MOSS name provided."
    exit 1
fi

# 根据MOSS和HFUnit设置几何配置文件
if [[ $MOSS == babyMOSS-* ]]; then
    if [[ $HFUnit == "tb" ]]; then
        GEOMETRY_FILE="${GEOMETRY_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_tb.conf"
    elif [[ $HFUnit == "bb" ]]; then
        GEOMETRY_FILE="${GEOMETRY_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_bb.conf"
    fi
elif [[ $MOSS == MOSS-* ]]; then
    if [[ $HFUnit =~ ^t[0-9]+$ ]]; then
        GEOMETRY_FILE="${GEOMETRY_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_top.conf"
    elif [[ $HFUnit =~ ^b[0-9]+$ ]]; then
        GEOMETRY_FILE="${GEOMETRY_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_bottom.conf"
    fi
fi

echo "Using geometry file: $GEOMETRY_FILE"
echo "Using config directory: $CONFIG_DIR"

# 确保更新目录存在
mkdir -p ${GEOMETRY_UPDATE_DIR}

# 记录脚本开始的时间
START_TOTAL=$(date +%s)

# 创建一个数组保存每个 region 的最小 VCASB 对应的 mask 文件
declare -A MASK_FILES

# 遍历所有region，找出每个 region 的最小 VCASB 文件夹
for REGION in 0 1 2 3; do
    DATA_DIR="/local/data/${TB_PERIOD}/${MOSS}/${HFUnit}_psub12/region${REGION}"
    
    # 找到当前region下最小的VCASB文件夹
    min_vcasb_dir=$(find ${DATA_DIR}/VCASB*/ -type d | sort -V | head -n 1)
    
    if [ -z "$min_vcasb_dir" ]; then
        echo "Warning: No VCASB directories found for Region $REGION. Skipping this region."
        continue  # 跳过当前region，继续下一个region的处理
    fi

    # 检查是否存在任何 .raw 文件
    raw_file_count=$(find "$min_vcasb_dir" -type f -name "*.raw" | wc -l)
    if [ "$raw_file_count" -eq 0 ]; then
        echo "Warning: No .raw files found for Region $REGION. Skipping this region."
        continue  # 跳过当前region，继续下一个region的处理
    fi

    min_vcasb=$(basename "$min_vcasb_dir")

    # 生成目标文件名
    GEOMETRY_UPDATE_FILE="${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${MOSS}_${HFUnit}_region${REGION}_${min_vcasb}_masked.conf"
    
    # 创建更新后的几何配置文件
    cp "${GEOMETRY_FILE}" "${GEOMETRY_UPDATE_FILE}"
    
    # 如果没有设置 --skip-mask，则添加 mask_file 行
    if [ "$SKIP_MASK" = false ]; then
        MASK_FILE_PATH="mask_files/masked_pixel_${MOSS}_${HFUnit}_reg${REGION}.txt"
        sed -i "/\[MOSS_reg${REGION}_3\]/a mask_file = \"${MASK_FILE_PATH}\"" "${GEOMETRY_UPDATE_FILE}"
    fi
    
    MASK_FILES[$REGION]="${GEOMETRY_UPDATE_FILE}"

    echo "Created geometry file with mask: ${GEOMETRY_UPDATE_FILE}"
done

# 遍历所有region
for REGION in 0 1 2 3; do
    # 获取min_vcasb_dir
    DATA_DIR="/local/data/${TB_PERIOD}/${MOSS}/${HFUnit}_psub12/region${REGION}"
    min_vcasb_dir=$(find ${DATA_DIR}/VCASB*/ -type d | sort -V | head -n 1)
    
    if [ -z "$min_vcasb_dir" ]; then
        echo "Warning: No VCASB directories found for Region $REGION. Skipping this region."
        continue
    fi

    # 查找最小VCASB文件夹中的raw data文件，并选取编号最大的文件
    min_raw_file=$(find "$min_vcasb_dir" -type f -name "*.raw" | sort -V | tail -n 1)

    # Debugging: 输出当前路径和文件
    echo "Region $REGION: min_vcasb_dir = $min_vcasb_dir"
    echo "Region $REGION: min_raw_file = $min_raw_file"

    if [ -z "$min_raw_file" ]; then
        echo "Warning: No .raw file found in $min_vcasb_dir, skipping Region $REGION."
        continue  # 跳过当前region，继续下一个region的处理
    fi
    
    SUFFIX_MIN="${MOSS}_${HFUnit}_region${REGION}_${min_vcasb}"
    OPT_FNAME_MIN="-o EventLoaderEUDAQ2.file_name=${min_raw_file}"
    OUTPUT_DIR_MIN="/local/analysis/output/${SUFFIX_MIN}"
    mkdir -p ${OUTPUT_DIR_MIN}

    if [ ! -f "${MASK_FILES[$REGION]}" ]; then
        echo "Error: The geometry file ${MASK_FILES[$REGION]} does not exist."
        exit 1
    fi

    # Debugging: Log the path to the geometry file and raw file
    echo "Using geometry file for region ${REGION}: ${MASK_FILES[$REGION]}"
    echo "Using raw file for region ${REGION}: ${min_raw_file}"

    corry -c ${CONFIG_DIR}/prealign.conf $OPT_FNAME_MIN \
          -o detectors_file=${MASK_FILES[$REGION]} \
          -o detectors_file_updated=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_prealigned.conf \
          -o histogram_file=prealignment.root \
          -o output_directory=${OUTPUT_DIR_MIN}

    corry -c ${CONFIG_DIR}/align.conf $OPT_FNAME_MIN \
          -g MOSS_reg0_3.role=passive \
          -g MOSS_reg1_3.role=passive \
          -g MOSS_reg2_3.role=passive \
          -g MOSS_reg3_3.role=passive \
          -o detectors_file=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_prealigned.conf \
          -o detectors_file_updated=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_refaligned.conf \
          -o histogram_file=refalignment.root \
          -o output_directory=${OUTPUT_DIR_MIN}

    # 使用最小VCASB文件进行refaligned到aligned的对准
    corry -c ${CONFIG_DIR}/align.conf $OPT_FNAME_MIN \
          -g MOSS_reg0_3.role=$( [ "$REGION" -eq 0 ] && echo "dut" || echo "auxiliary" ) \
          -g MOSS_reg1_3.role=$( [ "$REGION" -eq 1 ] && echo "dut" || echo "auxiliary" ) \
          -g MOSS_reg2_3.role=$( [ "$REGION" -eq 2 ] && echo "dut" || echo "auxiliary" ) \
          -g MOSS_reg3_3.role=$( [ "$REGION" -eq 3 ] && echo "dut" || echo "auxiliary" ) \
          -o detectors_file=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_refaligned.conf \
          -o detectors_file_updated=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_aligned.conf \
          -o histogram_file=alignment.root \
          -o output_directory=${OUTPUT_DIR_MIN}

    # 4. 使用最小VCASB的aligned几何配置进行分析
    for dir in ${DATA_DIR}/VCASB*/; do
    # 查找文件夹中的所有raw data文件
    raw_files=$(find "$dir" -type f -name "*.raw" | sort -V)
    
    if [ -z "$raw_files" ];then
        echo "No .raw files found in $dir, skipping."
        continue
    fi

    # 初始化计数器
    file_counter=0

    # 对每个找到的raw文件进行分析
    for raw_file in $raw_files; do
        # 提取VCASB后面的数字部分，作为SUFFIX的一部分
        VCASB=$(basename "$dir")
        SUFFIX="${MOSS}_${HFUnit}_region${REGION}_${VCASB}"

        OPT_FNAME="-o EventLoaderEUDAQ2.file_name=${raw_file}"
        
        OUTPUT_DIR="/local/analysis/output/${SUFFIX}"
        mkdir -p ${OUTPUT_DIR}

        START=$(date +%s)
        
        corry -c ${CONFIG_DIR}/analyse.conf $OPT_FNAME \
              -g MOSS_reg0_3.role=$( [ "$REGION" -eq 0 ] && echo "dut" || echo "auxiliary" ) \
              -g MOSS_reg1_3.role=$( [ "$REGION" -eq 1 ] && echo "dut" || echo "auxiliary" ) \
              -g MOSS_reg2_3.role=$( [ "$REGION" -eq 2 ] && echo "dut" || echo "auxiliary" ) \
              -g MOSS_reg3_3.role=$( [ "$REGION" -eq 3 ] && echo "dut" || echo "auxiliary" ) \
              -o detectors_file=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_aligned.conf \
              -o histogram_file=analysis_${VCASB}_${file_counter}.root \
              -o output_directory=${OUTPUT_DIR} \
              -l ${OUTPUT_DIR}/analysis_${VCASB}_${file_counter}.log

        END=$(date +%s)
        DIFF=$((END - START))
        
        echo "Analysis for $raw_file in Region $REGION completed in $DIFF seconds."

        # 增加计数器
        file_counter=$((file_counter + 1))
    done
done
done

# 记录脚本结束的时间
END_TOTAL=$(date +%s)
DIFF_TOTAL=$((END_TOTAL - START_TOTAL))

echo "Total time for the script: $DIFF_TOTAL seconds."