#!/bin/bash

# 定义环境变量
NUMJOBS=${1:-1}  # 默认为1，可以通过命令行参数覆盖
MODE=randread
BLOCK_SIZE=4M
FILESIZE=14G  # 文件大小

# 定义 iodepth 数组
iodepths=("1" "2" "4" "8" "16")

for IODEPTH in "${iodepths[@]}"; do
  # 创建配置文件
  cat << EOF > disktest-${IODEPTH}.fio
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
  output_file="disktest-${NUMJOBS}-${IODEPTH}.json"

  # 运行fio测试
  fio --output-format=json --output="${output_file}" disktest-${IODEPTH}.fio

  echo "Finished running fio with numjobs=${NUMJOBS} and iodepth=${IODEPTH}"
done
