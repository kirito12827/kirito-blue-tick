import os
import yaml
import requests
import shutil

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

def convert_file_to_yaml(file_path):
    """
    将指定文件转换为 .yaml 文件
    :param file_path: str, 需要转换的文件路径
    """
    file_data = read_file(file_path)
    yaml_filename = os.path.splitext(os.path.basename(file_path))[0] + '.yaml'
    yaml_path = os.path.join(os.path.dirname(file_path), yaml_filename)
    write_yaml(file_data, yaml_path)
    print(f"已将 {file_path} 转换为 {yaml_filename}")
    return yaml_path

def process_files(file_urls):
    """
    下载并处理文件
    :param file_urls: list, 文件的 URL 列表
    """
    for file_url in file_urls:
        file_name = file_url.split('/')[-1]
        download_file(file_url, file_name)

        # 创建以文件名为名的文件夹
        folder_name = os.path.splitext(file_name)[0]
        os.makedirs(folder_name, exist_ok=True)

        # 移动原始文件到文件夹中
        shutil.move(file_name, os.path.join(folder_name, file_name))

        # 转换文件并将 YAML 文件移动到相同文件夹中
        converted_file_path = convert_file_to_yaml(os.path.join(folder_name, file_name))
        shutil.move(converted_file_path, os.path.join(folder_name, os.path.basename(converted_file_path)))

if __name__ == "__main__":
    # 定义要下载的多个文件的URL列表
    file_urls = [
        "https://raw.githubusercontent.com/Coldvvater/Mononoke/refs/heads/master/Clash/Rules/DownloadCDN_CN.list",
        "https://raw.githubusercontent.com/Coldvvater/Mononoke/refs/heads/master/Clash/Rules/Emby.list"
    ]
    
    # 处理文件下载和转换
    process_files(file_urls)
