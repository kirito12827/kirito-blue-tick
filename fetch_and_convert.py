import os
import yaml
import requests

def download_file(file_url, save_path):
    """
    下载指定的文件
    :param file_url: str, 文件的URL
    :param save_path: str, 保存文件的路径
    """
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"文件已下载: {save_path}")
    else:
        print(f"下载失败: {file_url}, 状态码: {response.status_code}")

def read_file(file_path):
    """
    读取 .list 或 .txt 文件的内容
    :param file_path: str, 文件的路径
    :return: list, 文件的每一行作为列表元素返回
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    return [line.strip() for line in content]

def write_yaml(data, output_path):
    """
    将数据写入到 .yaml 文件
    :param data: list, 需要转换为 yaml 的数据
    :param output_path: str, 输出的 yaml 文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(data, yaml_file, allow_unicode=True, default_flow_style=False)

def convert_files_to_yaml(directory):
    """
    将目录中的 .list 和 .txt 文件自动转换为 .yaml 文件
    :param directory: str, 目录路径
    """
    for filename in os.listdir(directory):
        if filename.endswith('.list') or filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            print(f"正在处理文件: {file_path}")
            
            # 读取文件内容
            file_data = read_file(file_path)
            
            # 构造输出的 yaml 文件路径
            yaml_filename = os.path.splitext(filename)[0] + '.yaml'
            yaml_path = os.path.join(directory, yaml_filename)
            
            # 将内容写入 yaml 文件
            write_yaml(file_data, yaml_path)
            print(f"已将 {filename} 转换为 {yaml_filename}")

if __name__ == "__main__":
    # 定义要下载的多个文件的URL列表
    file_urls = [
        "https://raw.githubusercontent.com/Coldvvater/Mononoke/refs/heads/master/Clash/Rules/DownloadCDN_CN.list",
        "https://raw.githubusercontent.com/Coldvvater/Mononoke/refs/heads/master/Clash/Rules/Emby.list"
    ]
    
    # 下载每个文件并保存
    for file_url in file_urls:
        file_name = file_url.split('/')[-1]
        download_file(file_url, file_name)
    
    # 执行转换
    convert_files_to_yaml(".")
