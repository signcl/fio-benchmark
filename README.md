# fio-benchmark
- 针对磁盘性能BenchMark 说明文档



## 临时存储空间性能测试

### 利用 shell 脚本，针对不同场景分别生成不同的fio脚本命令来对磁盘进行benchmark

1. 项目的目录下，分别对应randread,randwrite,read,write 四个工作目录。修改脚本run_fio_2G.sh 中 `json_results_dir_name` 为: 默认为`env_json_results`。也就是如果不手动指定json数据存放目录，所有的
   数据都将存在env_json_results目录中。建议每次修改这个json的值。来存放不同环境的测试结果。

2. 注意测试的时候需要根据具体情况来修改脚本内容,默认值:
  - 1为任务数量
  - MODE 为fio测试模式，默认值为randread
  - BLOCK_SIZE 为测试数据块的大小，默认值为4k

3. 我们要测试什么模式的性能，就在对应的模式下benchmark。

- bash run_fio_2G.sh 这个脚本，会在每个测试模式下生成对于fio测试命令。
- bash run_fio_14G.sh 这个脚本，会在每个测试模式下生成对于fio测试命令。

具体的脚本，创建一个名为run_fio_tests.sh的文件，并chmod 赋予+x权限。执行该脚本就会在`env_json_results`目录下生成fio 测试的json文件

- 测试:

```
cd randread/
./run_fio_tests.sh 1 randread 4096k
```

- 脚本示例:
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


## 测试结果

- randread-4096k

|    | Job                      |   iodepth |   procs |   Read IOPS |   Write IOPS |   Read BW (GiB/s) |   Write BW (GiB/s) |
|---:|:-------------------------|----------:|--------:|------------:|-------------:|------------------:|-------------------:|
|  8 | 1-proc-randread-4096k-1  |         1 |       1 |     145.724 |            0 |           582.894 |                  0 |
|  2 | 1-proc-randread-4096k-2  |         2 |       1 |     307.036 |            0 |          1228.14  |                  0 |
|  5 | 1-proc-randread-4096k-4  |         4 |       1 |     401.393 |            0 |          1605.57  |                  0 |
|  4 | 1-proc-randread-4096k-8  |         8 |       1 |     461.146 |            0 |          1844.58  |                  0 |
|  0 | 1-proc-randread-4096k-16 |        16 |       1 |     481.019 |            0 |          1924.08  |                  0 |
|  3 | 4-proc-randread-4096k-1  |         1 |       4 |     332.8   |            0 |          1331.2   |                  0 |
|  9 | 4-proc-randread-4096k-2  |         2 |       4 |     483.776 |            0 |          1935.11  |                  0 |
|  6 | 4-proc-randread-4096k-4  |         4 |       4 |     520.729 |            0 |          2082.91  |                  0 |
|  7 | 4-proc-randread-4096k-8  |         8 |       4 |     541.66  |            0 |          2166.64  |                  0 |
|  1 | 4-proc-randread-4096k-16 |        16 |       4 |     547.553 |            0 |          2190.21  |                  0 |

- randread-4k

|    | Job                   |   iodepth |   procs |   Read IOPS |   Write IOPS |   Read BW (GiB/s) |   Write BW (GiB/s) |
|---:|:----------------------|----------:|--------:|------------:|-------------:|------------------:|-------------------:|
|  6 | 1-proc-randread-4k-1  |         1 |       1 |     4646.15 |            0 |           18.1484 |                  0 |
|  4 | 1-proc-randread-4k-2  |         2 |       1 |     9953.17 |            0 |           38.8789 |                  0 |
|  2 | 1-proc-randread-4k-4  |         4 |       1 |    18970.5  |            0 |           74.1035 |                  0 |
|  3 | 1-proc-randread-4k-8  |         8 |       1 |    32259    |            0 |          126.011  |                  0 |
|  1 | 1-proc-randread-4k-16 |        16 |       1 |    40101.5  |            0 |          156.646  |                  0 |
|  0 | 4-proc-randread-4k-1  |         1 |       4 |    18025.6  |            0 |           70.4121 |                  0 |
|  9 | 4-proc-randread-4k-2  |         2 |       4 |    35781.6  |            0 |          139.771  |                  0 |
|  8 | 4-proc-randread-4k-4  |         4 |       4 |    60906.5  |            0 |          237.916  |                  0 |
|  7 | 4-proc-randread-4k-8  |         8 |       4 |    81373.5  |            0 |          317.864  |                  0 |
|  5 | 4-proc-randread-4k-16 |        16 |       4 |    86845.4  |            0 |          339.239  |                  0 |


## 测试图表

![企业微信截图_293ff91a-7c25-446d-9f92-649dd852f3e7](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_293ff91a-7c25-446d-9f92-649dd852f3e7.png)

![企业微信截图_d4d0959a-f46d-48fa-8991-b6eff2006702](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_d4d0959a-f46d-48fa-8991-b6eff2006702.png)

![企业微信截图_f6efefc5-27c1-4056-ae00-26f53d38db93](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_f6efefc5-27c1-4056-ae00-26f53d38db93.png)


![企业微信截图_579e71b6-0607-47fe-9469-0769aa0d889b](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_579e71b6-0607-47fe-9469-0769aa0d889b.png)

![企业微信截图_e9ebf4d4-0fcf-4ae8-be71-82bc3beb7d17](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_e9ebf4d4-0fcf-4ae8-be71-82bc3beb7d17.png)

![企业微信截图_ef435e2c-5a35-4d71-ab4b-3da4a708f9c0](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_ef435e2c-5a35-4d71-ab4b-3da4a708f9c0.png)

![企业微信截图_63770cba-08a5-43dc-986b-972016c00e1a](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_63770cba-08a5-43dc-986b-972016c00e1a.png)

![企业微信截图_36ed7368-aa6c-4676-a3ec-130c5ed4ddcd](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_36ed7368-aa6c-4676-a3ec-130c5ed4ddcd.png)


- 14G 文件测试
![企业微信截图_9f19be07-b6d2-4db5-a583-9b910c86814b](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_9f19be07-b6d2-4db5-a583-9b910c86814b.png)

![企业微信截图_90da2ff4-c50a-43f4-ad99-3057e0762630](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_90da2ff4-c50a-43f4-ad99-3057e0762630.png)

![企业微信截图_560ac024-211a-4318-a6d2-c787d0b10d49](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/企业微信截图_560ac024-211a-4318-a6d2-c787d0b10d49.png)

![20240806163640](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240806163640.png)


## 小算图表

![20240807155858](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807155858.png)

![20240807155958](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807155958.png)

![20240807160243](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807160243.png)

![20240807160359](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807160359.png)

![20240807160809](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807160809.png)

![20240807160959](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807160959.png)

![20240807161117](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807161117.png)

![20240807161156](https://barry-boy-1311671045.cos.ap-beijing.myqcloud.com/blog/20240807161156.png)


## 文章参考

- [openbayes 磁盘测试](https://openbayes.com/docs/runtimes/storage-perf/)