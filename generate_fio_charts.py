import json
import os
import pandas as pd
import plotly.graph_objects as go
from tabulate import tabulate

# 定义读取 JSON 文件并解析数据的函数
def parse_fio_json(file_path, mode):
    with open(file_path, 'r') as f:
        data = json.load(f)
    job_name = os.path.basename(file_path).replace('.json', '')
    parts = job_name.split('-')
    if mode in ['randread', 'read']:
        iops = data['jobs'][0]['read']['iops']  # IOPS 默认单位是 ops/s，不需要转换
        bw = data['jobs'][0]['read']['bw'] / 1048576  # 将 KB/s 转换为 GiB/s
    else:  # randwrite, write
        iops = data['jobs'][0]['write']['iops']  # IOPS 默认单位是 ops/s，不需要转换
        bw = data['jobs'][0]['write']['bw'] / 1048576  # 将 KB/s 转换为 GiB/s
    procs = int(parts[0])
    iodepth = int(parts[-1])
    return job_name, iodepth, procs, iops, bw

# 定义生成图表的函数
def generate_charts(data, output_dir, output_filename, mode, size):
    df = pd.DataFrame(data, columns=['Job', 'iodepth', 'procs', 'IOPS', 'BW (GiB/s)'])
    df = df.sort_values(by=['procs', 'iodepth'])

    fig = go.Figure()

    # 添加 IOPS 线条
    for proc in df['procs'].unique():
        subset = df[df['procs'] == proc]
        fig.add_trace(go.Scatter(x=subset['iodepth'], y=subset['IOPS'], mode='lines+markers', name=f'IOPS: procs={proc}'))

    # 添加 BW 线条
    for proc in df['procs'].unique():
        subset = df[df['procs'] == proc]
        fig.add_trace(go.Scatter(x=subset['iodepth'], y=subset['BW (GiB/s)'], mode='lines+markers', name=f'BW: procs={proc}', yaxis='y2'))

    fig.update_layout(
        title={
            'text': f"IOPS and Bandwidth vs iodepth ({mode} {size})",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title="iodepth",
            type="category",
            tickvals=[1, 2, 4, 8, 16],
            ticktext=["1", "2", "4", "8", "16"]
        ),
        yaxis_title="IOPS",
        yaxis2=dict(title="BW (GiB/s)", overlaying='y', side='right'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        width=800,
        height=400
    )

    html_filename = os.path.join(output_dir, f'{output_filename}.html')
    fig.write_html(html_filename)

    return df, html_filename

# 主函数
def main(json_dir, output_dir, mode, size):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    data = []
    for root, dirs, files in os.walk(json_dir):
        for json_file in files:
            if json_file.endswith('.json'):
                file_path = os.path.join(root, json_file)
                job_name, iodepth, procs, iops, bw = parse_fio_json(file_path, mode)
                data.append([job_name, iodepth, procs, iops, bw])
    output_filename = f'iops_bw_{mode}_{size}_chart_plotly'
    df, html_filepath = generate_charts(data, output_dir, output_filename, mode, size)
    return df, html_filepath

# 设置 JSON 文件所在目录和输出图表的目录
# json_dirs = {
#     'randread-4k': './cephfs-benchmark/dataset-bench/json_results/randread-4k',
#     'randread-4M': './cephfs-benchmark/dataset-bench/json_results/randread-4M',
#     'read-4096k': './cephfs-benchmark/dataset-bench/json_results/read-4096k',
#     'read-4k': './cephfs-benchmark/dataset-bench/json_results/read-4k',
# }
# json_dirs = {
#     'randread-4k': './randread/env_json_results/randread-4k',
#     'randread-4096k': './randread/env_json_results/randread-4096k',
#     'randwrite-4k': './randwrite/env_json_results/randwrite-4k',
#     'randwrite-4096k': './randwrite/env_json_results/randwrite-4096k',
#     'read-4k': './read/env_json_results/read-4k',
#     'read-4096k': './read/env_json_results/read-4096k',
#     'write-4k': './write/env_json_results/write-4k',
#     'write-4096k': './write/env_json_results/write-4096k'
# }

json_dirs = {
    'randread-4k': './randread/cmft_14G_json_results/randread-4k',
    'randread-4M': './randread/cmft_14G_json_results/randread-4M',
    'read-4096k': './read/cmft_14G_json_results/read-4096k',
    'read-4k': './read/cmft_14G_json_results/read-4k',
}

# json_dirs = {
#     'randread-4k': './randread/cmft_2G_json_results/randread-4k',
#     'randread-4096k': './randread/cmft_2G_json_results/randread-4096k',
#     'randwrite-4k': './randwrite/cmft_2G_json_results/randwrite-4k',
#     'randwrite-4096k': './randwrite/cmft_2G_json_results/randwrite-4096k',
#     'read-4k': './read/cmft_2G_json_results/read-4k',
#     'read-4096k': './read/cmft_2G_json_results/read-4096k',
#     'write-4k': './write/cmft_2G_json_results/write-4k',
#     'write-4096k': './write/cmft_2G_json_results/write-4096k'
# }
output_dir = './charts/cmft_14G_output_charts'  # 替换为您希望保存图表的目录

# 运行主函数并显示结果
for key, json_dir in json_dirs.items():
    mode = key.split('-')[0]  # 获取模式
    size = key.split('-')[1]  # 获取块大小
    df, html_filepath = main(json_dir, output_dir, mode, size)
    markdown_output = df.to_markdown()
    print(markdown_output)

    # 保存 Markdown 输出到文件
    markdown_filename = os.path.join(output_dir, f'{key}.md')
    with open(markdown_filename, 'w') as f:
        f.write(markdown_output)