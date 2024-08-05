# fio-benchmark
- 针对磁盘性能BenchMark 说明文档



## 临时存储空间性能测试

### 利用 shell 脚本，针对不同场景分别生成不同的fio脚本命令来对磁盘进行benchmark

1. 创建一个测试目录`json_results`，用来存放生成的json数据
2. 注意测试的时候需要根据具体情况来修改脚本内容,默认值:
  - 1为任务数量
  - MODE 为fio测试模式，默认值为randread
  - BLOCK_SIZE 为测试数据块的大小，默认值为4k

具体的脚本，创建一个名为run_fio_tests.sh的文件，并chmod 赋予+x权限。执行该脚本就会在`json_results`目录下生成fio 测试的json文件

```
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
  config_file="${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}.fio"

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

  echo "Finished running fio with numjobs=${NUMJOBS}, rw=${MODE}, bs=${BLOCK_SIZE}, and iodepth=${IODEPTH}"
done
```


### 使用说明

1.	NUMJOBS：默认为1，可以通过命令行参数进行覆盖。例如，若要使用4，可以运行脚本时传递参数 ./run_fio_tests.sh 4。
2.	MODE：读写模式，默认为 randread，可以通过命令行参数进行覆盖。例如，若要使用 randwrite，可以运行脚本时传递参数 ./run_fio_tests.sh 1 randwrite。
3.	BLOCK_SIZE：块大小，默认为 4k，可以通过命令行参数进行覆盖。例如，若要使用 4M，可以运行脚本时传递参数 ./run_fio_tests.sh 1 randread 4M。
4.	FILESIZE：文件大小，指定为 2G，与您的文件大小一致。
5.	OUTPUT_DIR：存放 JSON 文件的目录，默认为 json_results。


### 运行脚本

```
./run_fio_tests.sh 1 randread 4096k
./run_fio_tests.sh 4 randwrite 4M


./run_fio_tests.sh 1 randread 4096k && ./run_fio_tests.sh 4 randread 4096k && ./run_fio_tests.sh 1 randread 4k && ./run_fio_tests.sh 4 randread 4k

./run_fio_tests.sh 1 randwrite 4096k && ./run_fio_tests.sh 4 randwrite 4096k && ./run_fio_tests.sh 1 randwrite 4k && ./run_fio_tests.sh 4 randwrite 4k

./run_fio_tests.sh 1 read 4096k && ./run_fio_tests.sh 4 read 4096k && ./run_fio_tests.sh 1 read 4k && ./run_fio_tests.sh 4 read 4k

./run_fio_tests.sh 1 write 4096k && ./run_fio_tests.sh 4 write 4096k && ./run_fio_tests.sh 1 write 4k && ./run_fio_tests.sh 4 write 4k
```

### 文件名和配置文件

•	根据 numjobs、rw 和 bs 参数生成相应的配置文件，例如 1-proc-randread-4k.fio。
•	输出文件名包含 numjobs、rw、bs 和 iodepth，例如 1-proc-randread-4k-1.json。
•	JSON 文件存放在 json_results 目录中。

这个脚本将自动生成和运行包含不同 iodepth 值的 fio 测试，并将结果保存到指定目录中的相应 JSON 文件中。每个测试完成后，脚本会输出一条完成信息，以便跟踪进度



## 数据集性能测试

1. 以下是针对数据集目录来测试，主要针对共享文件存储Cephfs。
2. 用法同上

```
#!/bin/bash

# 定义环境变量
NUMJOBS=${1:-1}  # 默认为1，可以通过命令行参数覆盖
MODE=${2:-randread}  # 默认为randread，可以通过命令行参数覆盖
BLOCK_SIZE=${3:-4k}  # 默认为4k，可以通过命令行参数覆盖
FILESIZE=14G  # 文件大小
OUTPUT_DIR="json_results"  # JSON 文件存放目录

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 定义 iodepth 数组
iodepths=("1" "2" "4" "8" "16")

for IODEPTH in "${iodepths[@]}"; do
  # 创建配置文件名称
  config_file="${NUMJOBS}-proc-${MODE}-${BLOCK_SIZE}.fio"

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
```




## 文章参考

- [openbayes 磁盘测试](https://openbayes.com/docs/runtimes/storage-perf/)