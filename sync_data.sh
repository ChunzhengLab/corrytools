#!/bin/bash

# 定义变量
BASE_PATH="2024-09_PS"
MOSS_NAME=""
REMOTE_USER="chunzhen"
REMOTE_HOST="lxplus.cern.ch"
REMOTE_BASE_DIR="/eos/project/a/aliceits3/ITS3-WP3/Testbeams"
LOCAL_BASE_DIR="/Users/wangchunzheng/works/moss_tool/data"

# 第一个 rsync 目录
REMOTE_DIR_1="$REMOTE_BASE_DIR/$BASE_PATH/$MOSS_NAME"
LOCAL_DIR_1="$LOCAL_BASE_DIR/2024-08_PS_II/"

# 第二个 rsync 目录
REMOTE_DIR_2="$REMOTE_BASE_DIR/$BASE_PATH/MOSS_TEST_RESULTS/$MOSS_NAME"
LOCAL_DIR_2="$LOCAL_BASE_DIR/2024-08_PS_II/MOSS_TEST_RESULTS/"

# 提示用户确认
echo "Are you sure? Have you checked the path name?"
read -p "Enter Y to continue: " confirmation

# 检查用户输入
if [[ "$confirmation" != "Y" ]]; then
    echo "Operation aborted."
    exit 1
fi

# 同步第一个目录
rsync -avz --progress --include='*.json' --include='*.json5' --include='*.raw' --exclude='*' "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR_1" "$LOCAL_DIR_1"

# 同步第二个目录
rsync -avz --progress --include='*.json' --include='*.json5' --include='*.raw' --exclude='*' "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR_2" "$LOCAL_DIR_2"