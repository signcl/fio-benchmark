#!/bin/bash

# 定义参数
config_file="1-proc-randread-4096k.fio"
base_output="1"
rw="randread"
bs="4096k"
iodepths=("1" "2" "4" "8" "16")

# 备份原始配置文件
cp $config_file "${config_file}.bak"

for iodepth in "${iodepths[@]}"; do
  # 修改配置文件中的 iodepth 值
  sed -i "s/^iodepth=.*/iodepth=${iodepth}/" $config_file
  
  # 定义输出文件名称
  output_file="${base_output}-${iodepth}-${rw}-${bs}.json"
  
  # 运行fio命令
  fio --output-format=json --output="$output_file" "$config_file"
  
  echo "Finished running $config_file with iodepth=$iodepth"
done

# 还原原始配置文件
mv "${config_file}.bak" $config_file

