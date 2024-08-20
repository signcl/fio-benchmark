#!/bin/bash

# 定义需要处理的目录列表
directories=("randread" "randwrite" "read" "write")

# 获取当前工作目录
current_dir=$(pwd)

# 循环遍历每个目录
for dir in "${directories[@]}"; do
  # 检查并创建目录
  if [ ! -d "$current_dir/$dir" ]; then
    mkdir -p "$current_dir/$dir"
    echo "Directory $dir created."
  fi

  # 在当前目录下创建 JSON 结果目录
  json_results_dir="$current_dir/$dir/$json_results_dir_name"
  mkdir -p "$json_results_dir"
  echo "JSON results directory $json_results_dir created."

  # 创建脚本
  cat << 'EOF' > "$current_dir/$dir/run_fio_tests.sh"
#!/bin/bash

# 定义环境变量
NUMJOBS=\${1:-1}  # 默认为1，可以通过命令行参数覆盖
MODE=\${2:-randread}  # 默认为randread，可以通过命令行参数覆盖
BLOCK_SIZE=\${3:-4k}  # 默认为4k，可以通过命令行参数覆盖
FILESIZE=2G  # 文件大小

# 根据模式和块大小定义输出目录
OUTPUT_DIR="./${OUTPUT_BASE_DIR}/${MODE}-${BLOCK_SIZE}"

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 定义 iodepth 数组
iodepths=("1" "2" "4" "8" "16")

for IODEPTH in "${iodepths[@]}"; do
  # 创建配置文件名称
  config_file="${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}-${IODEPTH}.fio"

  # 创建配置文件
  cat << EOF2 > $config_file
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
EOF2

  # 定义输出文件名称
  output_file="${OUTPUT_DIR}/${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}-${IODEPTH}.json"

  # 运行fio测试
  fio --output-format=json --output="$output_file" $config_file

  # 输出完成信息
  echo "Prepared to run fio with numjobs=${NUMJOBS}, rw=${MODE}, bs=${BLOCK_SIZE}, and iodepth=${IODEPTH}"
done
EOF

  # 设置脚本可执行权限
  chmod +x "$current_dir/$dir/run_fio_tests.sh"

done