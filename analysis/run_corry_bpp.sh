#!/bin/bash

# 初始化标志变量
SKIP_MASK=false
HIGHSTAT=false
ONLY_ANALYSE=false
REGION0=false
REGION1=false
REGION2=false
REGION3=false

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
        --high-stat)
            HIGHSTAT=true
            shift
            ;;
        --only-analyse)
            ONLY_ANALYSE=true
            shift
            ;;
        --region0)
            REGION0=true
            shift
            ;;
        --region1)
            REGION1=true
            shift
            ;;
        --region2)
            REGION2=true
            shift
            ;;
        --region3)
            REGION3=true
            shift
            ;;
        babyMOSS-2_2_W21D4 | MOSS-3_W08B6 | MOSS-2_W02F4 | babyMOSS-2_3_W04E2 | babyMOSS-2_3_W24B5)
            MOSS=$1
            shift
            ;;
        t[0-9]* | b[0-9]* | bb | tb)
            HFUnit=$1
            shift
            ;;
        *)
            echo "Usage: $0 [--skip-mask] [--high-stat] [--only-analyse] [--region0] [--region1] [--region2] [--region3] <babyMOSS-2_2_W21D4 or MOSS-3_W08B6 or MOSS-2_W02F4 or babyMOSS-2_3_W04E2 or babyMOSS-2_3_W24B5> <tN or nN or bb or tb>"
            exit 1
            ;;
    esac
done

# 检查必要的参数是否提供
if [ -z "$MOSS" ] || [ -z "$HFUnit" ]; then
    echo "Error: MOSS name and HFUnit must be provided."
    echo "Usage: $0 [--skip-mask] [--high-stat] [--only-analyse] [--region0] [--region1] [--region2] [--region3] <babyMOSS-2_2_W21D4 or MOSS-3_W08B6 or MOSS-2_W02F4 or babyMOSS-2_3_W04E2 or babyMOSS-2_3_W24B5> <tN or nN or bb or tb>"
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

# 创建一个数组保存每个 region 的最小 VCASB 对应的 mask 文件和 VCASB 值
declare -A MASK_FILES
declare -A MIN_VCASB

# 确定需要分析的区域
REGIONS=()
if [ "$REGION0" = true ]; then
    REGIONS+=(0)
fi
if [ "$REGION1" = true ]; then
    REGIONS+=(1)
fi
if [ "$REGION2" = true ]; then
    REGIONS+=(2)
fi
if [ "$REGION3" = true ]; then
    REGIONS+=(3)
fi

# 如果没有指定任何区域，则默认分析所有区域
if [ ${#REGIONS[@]} -eq 0 ]; then
    REGIONS=(0 1 2 3)
fi

# 遍历指定的区域
for REGION in "${REGIONS[@]}"; do
    # 如果启用了 highstat，修改 DATA_DIR
    if [ "$HIGHSTAT" = true ]; then
        DATA_DIR="/local/data/${TB_PERIOD}/${MOSS}/${HFUnit}_psub12_highstat/region${REGION}"
    else
        DATA_DIR="/local/data/${TB_PERIOD}/${MOSS}/${HFUnit}_psub12/region${REGION}"
    fi
    
    # 找到当前region下最小的VCASB文件夹
    min_vcasb_dir=$(find ${DATA_DIR}/VCASB*/ -type d | sort -V | head -n 1)
    
    if [ -z "$min_vcasb_dir" ]; then
        echo "Warning: No VCASB directories found for Region $REGION. Skipping this region."
        continue
    fi

    # 检查是否存在任何 .raw 文件
    raw_file_count=$(find "$min_vcasb_dir" -type f -name "*.raw" | wc -l)
    if [ "$raw_file_count" -eq 0 ]; then
        echo "Warning: No .raw files found for Region $REGION. Skipping this region."
        continue
    fi

    # 生成目标文件名，去掉 VCASB 值
    if [ "$HIGHSTAT" = true ]; then
        GEOMETRY_UPDATE_FILE="${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${MOSS}_${HFUnit}_region${REGION}_highstat_masked.conf"
    else
        GEOMETRY_UPDATE_FILE="${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${MOSS}_${HFUnit}_region${REGION}_masked.conf"
    fi
    
    # 创建更新后的几何配置文件
    if [ "$ONLY_ANALYSE" = false ]; then
        cp "${GEOMETRY_FILE}" "${GEOMETRY_UPDATE_FILE}"
    
        # 如果没有设置 --skip-mask，则添加 mask_file 行
        if [ "$SKIP_MASK" = false ]; then
            MASK_FILE_PATH="mask_files/masked_pixel_${MOSS}_${HFUnit}_reg${REGION}.txt"
            sed -i "/\[MOSS_reg${REGION}_3\]/a mask_file = \"${MASK_FILE_PATH}\"" "${GEOMETRY_UPDATE_FILE}"
        fi
    
        MASK_FILES[$REGION]="${GEOMETRY_UPDATE_FILE}"

        echo "Created geometry file with mask: ${GEOMETRY_UPDATE_FILE}"
    fi
done

# 遍历所有指定的 region 进行处理和分析
for REGION in "${REGIONS[@]}"; do
    # 获取每个region的最小VCASB号
    min_vcasb=${MIN_VCASB[$REGION]}
    
    # 获取数据目录
    if [ "$HIGHSTAT" = true ]; then
        DATA_DIR="/local/data/${TB_PERIOD}/${MOSS}/${HFUnit}_psub12_highstat/region${REGION}"
    else
        DATA_DIR="/local/data/${TB_PERIOD}/${MOSS}/${HFUnit}_psub12/region${REGION}"
    fi
    
    min_vcasb_dir="${DATA_DIR}/$min_vcasb"
    
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
        continue
    fi
    
    SUFFIX_MIN="${MOSS}_${HFUnit}_region${REGION}"
    OPT_FNAME_MIN="-o EventLoaderEUDAQ2.file_name=${min_raw_file}"
    
    if [ "$HIGHSTAT" = true ]; then
        OUTPUT_DIR_MIN="/local/analysis/output/${SUFFIX_MIN}_highstat"
    else
        OUTPUT_DIR_MIN="/local/analysis/output/${SUFFIX_MIN}"
    fi
    mkdir -p ${OUTPUT_DIR_MIN}

    DETECTORS_FILE="${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_aligned.conf"

    echo "ONLY_ANALYSE: $ONLY_ANALYSE"
    echo "DETECTORS_FILE: $DETECTORS_FILE"
    echo "DETECTORS_FILE exists: $(test -f "$DETECTORS_FILE" && echo "yes" || echo "no")"

    if [ "$ONLY_ANALYSE" = true ] && [ -f "$DETECTORS_FILE" ]; then
        echo "Skipping alignment for Region $REGION since detectors_file exists: $DETECTORS_FILE"
    else
        echo "Proceeding with alignment for Region $REGION"
        
        # 执行prealign，并检查其是否成功
        corry -c ${CONFIG_DIR}/prealign.conf $OPT_FNAME_MIN \
              -o detectors_file=${MASK_FILES[$REGION]} \
              -o detectors_file_updated=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_prealigned.conf \
              -o histogram_file=prealignment.root \
              -o output_directory=${OUTPUT_DIR_MIN} || { echo "Prealign step failed for Region $REGION"; exit 1; }

        # 执行对齐过程
        corry -c ${CONFIG_DIR}/align.conf $OPT_FNAME_MIN \
              -g MOSS_reg0_3.role=passive \
              -g MOSS_reg1_3.role=passive \
              -g MOSS_reg2_3.role=passive \
              -g MOSS_reg3_3.role=passive \
              -o detectors_file=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_prealigned.conf \
              -o detectors_file_updated=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_refaligned.conf \
              -o histogram_file=refalignment.root \
              -o output_directory=${OUTPUT_DIR_MIN} || { echo "Alignment step failed for Region $REGION"; exit 1; }

        # 使用通用 aligned 文件进行最终对准
        corry -c ${CONFIG_DIR}/align.conf $OPT_FNAME_MIN \
              -g MOSS_reg0_3.role=$( [ "$REGION" -eq 0 ] && echo "dut" || echo "auxiliary" ) \
              -g MOSS_reg1_3.role=$( [ "$REGION" -eq 1 ] && echo "dut" || echo "auxiliary" ) \
              -g MOSS_reg2_3.role=$( [ "$REGION" -eq 2 ] && echo "dut" || echo "auxiliary" ) \
              -g MOSS_reg3_3.role=$( [ "$REGION" -eq 3 ] && echo "dut" || echo "auxiliary" ) \
              -o detectors_file=${GEOMETRY_UPDATE_DIR}/${TB_PERIOD}_3REF-MOSS-3REF_${SUFFIX_MIN}_refaligned.conf \
              -o detectors_file_updated=${DETECTORS_FILE} \
              -o histogram_file=alignment.root \
              -o output_directory=${OUTPUT_DIR_MIN} || { echo "Final alignment step failed for Region $REGION"; exit 1; }
    fi

    # 4. 使用通用的 aligned 文件进行分析
    for dir in ${DATA_DIR}/VCASB*/; do
        # 查找文件夹中的所有raw data文件
        raw_files=$(find "$dir" -type f -name "*.raw" | sort -V)
        
        if [ -z "$raw_files" ]; then
            echo "No .raw files found in $dir, skipping."
            continue
        fi

        # 初始化计数器
        file_counter=0

        # 对每个找到的raw文件进行分析
        for raw_file in $raw_files; do
            # 提取VCASB后面的数字部分，作为SUFFIX的一部分
            VCASB=$(basename "$dir")
            if [ "$HIGHSTAT" = true ]; then
                SUFFIX="${MOSS}_${HFUnit}_region${REGION}_${VCASB}_highstat"
            else
                SUFFIX="${MOSS}_${HFUnit}_region${REGION}_${VCASB}"
            fi

            OPT_FNAME="-o EventLoaderEUDAQ2.file_name=${raw_file}"
            
            OUTPUT_DIR="/local/analysis/output/${SUFFIX}"
            mkdir -p ${OUTPUT_DIR}

            START=$(date +%s)

            # 根据 HFUnit 设置 inpixel_bin_size
            if [ "$HFUnit" = "tb" ]; then
                BIN_SIZE_OPTION="-o AnalysisDUT.inpixel_bin_size=2.5um -o AnalysisEfficiency.inpixel_bin_size=2.5um"
            elif [ "$HFUnit" = "bb" ]; then
                BIN_SIZE_OPTION="-o AnalysisDUT.inpixel_bin_size=2.0um -o AnalysisEfficiency.inpixel_bin_size=2.0um"
            else
                BIN_SIZE_OPTION=""
            fi
            
            corry -c ${CONFIG_DIR}/analyse.conf $OPT_FNAME \
                  -g MOSS_reg0_3.role=$( [ "$REGION" -eq 0 ] && echo "dut" || echo "auxiliary" ) \
                  -g MOSS_reg1_3.role=$( [ "$REGION" -eq 1 ] && echo "dut" || echo "auxiliary" ) \
                  -g MOSS_reg2_3.role=$( [ "$REGION" -eq 2 ] && echo "dut" || echo "auxiliary" ) \
                  -g MOSS_reg3_3.role=$( [ "$REGION" -eq 3 ] && echo "dut" || echo "auxiliary" ) \
                  -o detectors_file=${DETECTORS_FILE} \
                  -o histogram_file=analysis_${VCASB}_${file_counter}.root \
                  -o output_directory=${OUTPUT_DIR} \
                  -l ${OUTPUT_DIR}/analysis_${VCASB}_${file_counter}.log \
                  $BIN_SIZE_OPTION

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