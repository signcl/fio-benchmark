#!/bin/bash

# 定义需要处理的目录列表
directories=("randread" "randwrite" "read" "write")

# 获取当前工作目录
current_dir=$(pwd)

# 循环遍历每个目录
for dir in "${directories[@]}"; do
  # 创建脚本
  cat << 'EOL' > "$current_dir/$dir/run_fio_tests.sh"
#!/bin/bash

# 定义环境变量
NUMJOBS=${1:-1}  # 默认为1，可以通过命令行参数覆盖
MODE=${2:-randread}  # 默认为randread，可以通过命令行参数覆盖
BLOCK_SIZE=${3:-4k}  # 默认为4k，可以通过命令行参数覆盖
FILESIZE=2G  # 文件大小
OUTPUT_DIR="json_results"  # JSON 文件存放目录

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
size=${FILESIZE}
runtime=30
time_based
group_reporting
EOF

  # 定义输出文件名称
  output_file="${OUTPUT_DIR}/${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}-${IODEPTH}.json"

  # 运行fio测试
  fio --output-format=json --output="${output_file}" $config_file

  # 输出完成信息
  echo "Prepared to run fio with numjobs=${NUMJOBS}, rw=${MODE}, bs=${BLOCK_SIZE}, and iodepth=${IODEPTH}"
done
EOL

  # 设置脚本可执行权限
  chmod +x "$current_dir/$dir/run_fio_tests.sh"

done
