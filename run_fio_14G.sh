#!/bin/bash

# 定义环境变量
NUMJOBS=${1:-1}  # 默认为1，可以通过命令行参数覆盖
MODE=${2:-randread}  # 默认为randread，可以通过命令行参数覆盖
BLOCK_SIZE=${3:-4k}  # 默认为4k，可以通过命令行参数覆盖
FILESIZE=14G  # 文件大小

# 根据模式和块大小定义输出目录
OUTPUT_DIR="./json_results/${MODE}-${BLOCK_SIZE}"

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 定义 iodepth 数组
iodepths=("1" "2" "4" "8" "16")

for IODEPTH in "${iodepths[@]}"; do
  # 创建配置文件名称
  config_file="${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}-${IODEPTH}.fio"

  # 创建配置文件
  cat << EOF > $config_file
[disktest]
ioengine=libaio
iodepth=${IODEPTH}
numjobs=${NUMJOBS}
rw=${MODE}
bs=${BLOCK_SIZE}
direct=1
buffered=0
filename=$PWD/train.zip
size=${FILESIZE}
runtime=30
time_based
group_reporting
EOF

  # 定义输出文件名称
  output_file="${OUTPUT_DIR}/${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}-${IODEPTH}.json"

  # 运行fio测试
  fio --output-format=json --output="${output_file}" $config_file

  echo "Finished running fio with numjobs=${NUMJOBS}, rw=${MODE}, bs=${BLOCK_SIZE}, and iodepth=${IODEPTH}"
done