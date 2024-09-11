#!/bin/bash

# 输出开始时间年月日时分秒
echo "Start time: `date +%Y-%m-%d,%H:%M:%S`"

bash run_corry_bp.sh --skip-mask --high-stat --only-analyse babyMOSS-2_2_W21D4 tb

echo "task 1 is complete."

echo "All tasks are complete."

# 输出结束时间和运行时间
echo "End time: `date +%Y-%m-%d,%H:%M:%S`"
