import json
import os
import pandas as pd
import plotly.graph_objects as go
from tabulate import tabulate

# 定义读取 JSON 文件并解析数据的函数
def parse_fio_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    job_name = os.path.basename(file_path).replace('.json', '')
    parts = job_name.split('-')
    read_iops = data['jobs'][0]['read']['iops']
    write_iops = data['jobs'][0]['write']['iops']
    read_bw = data['jobs'][0]['read']['bw'] / 1024  # 转换为 GiB/s
    write_bw = data['jobs'][0]['write']['bw'] / 1024  # 转换为 GiB/s
    procs = int(parts[0])
    iodepth = int(parts[-1])
    return job_name, iodepth, procs, read_iops, write_iops, read_bw, write_bw

# 定义生成图表的函数
def generate_charts(data, output_dir):
    df = pd.DataFrame(data, columns=['Job', 'iodepth', 'procs', 'Read IOPS', 'Write IOPS', 'Read BW (GiB/s)', 'Write BW (GiB/s)'])
    df = df.sort_values(by=['procs', 'iodepth'])

    fig = go.Figure()

    # 添加 IOPS 线条
    for proc in df['procs'].unique():
        subset = df[df['procs'] == proc]
        fig.add_trace(go.Scatter(x=subset['iodepth'], y=subset['Read IOPS'], mode='lines+markers', name=f'IOPS: procs={proc}'))

    # 添加 BW 线条
    for proc in df['procs'].unique():
        subset = df[df['procs'] == proc]
        fig.add_trace(go.Scatter(x=subset['iodepth'], y=subset['Read BW (GiB/s)'], mode='lines+markers', name=f'BW: procs={proc}', yaxis='y2'))

    fig.update_layout(
        title="IOPS and Bandwidth vs iodepth",
        xaxis_title="iodepth",
        yaxis_title="IOPS",
        yaxis2=dict(title="BW (GiB/s)", overlaying='y', side='right'),
        width=800,
        height=400
    )

    fig.write_html(os.path.join(output_dir, 'iops_bw_4k_chart_plotly.html'))

    return df

# 主函数
def main(json_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    data = []
    for root, dirs, files in os.walk(json_dir):
        for json_file in files:
            if json_file.endswith('.json'):
                file_path = os.path.join(root, json_file)
                job_name, iodepth, procs, read_iops, write_iops, read_bw, write_bw = parse_fio_json(file_path)
                data.append([job_name, iodepth, procs, read_iops, write_iops, read_bw, write_bw])
    df = generate_charts(data, output_dir)
    return df

# 设置 JSON 文件所在目录和输出图表的目录
json_dir = './randread/json_results/randread-4k'  # 替换为您的 JSON 文件所在目录
output_dir = './output_charts'  # 替换为您希望保存图表的目录

# 运行主函数并显示结果
df = main(json_dir, output_dir)
markdown_output = df.to_markdown()
print(markdown_output)
