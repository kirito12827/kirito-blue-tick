import os
import requests
import shutil
import hashlib

def download_file(file_url, save_path):
    """
    下载指定的文件
    :param file_url: str, 文件的URL
    :param save_path: str, 保存文件的路径
    :return: bool, 文件是否下载且内容有变化
    """
    response = requests.get(file_url)
    if response.status_code == 200:
        # 如果文件存在，计算现有文件的哈希值
        if os.path.exists(save_path):
            with open(save_path, 'rb') as existing_file:
                existing_hash = hashlib.md5(existing_file.read()).hexdigest()
        else:
            existing_hash = None

        # 保存下载的文件并计算哈希值
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"文件已下载: {save_path}")

        with open(save_path, 'rb') as new_file:
            new_hash = hashlib.md5(new_file.read()).hexdigest()

        # 比较新旧文件的哈希值
        if existing_hash == new_hash:
            print(f"文件未更新: {save_path}")
            return False  # 文件没有变化
        else:
            print(f"文件已更新: {save_path}")
            return True  # 文件有变化
    else:
        print(f"下载失败: {file_url}, 状态码: {response.status_code}")
        return False

def read_file(file_path):
    """
    读取 .list 或 .txt 文件的内容
    :param file_path: str, 文件的路径
    :return: list, 文件的每一行作为列表元素返回
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    return [line.strip() for line in content]  # 返回所有行

def write_custom_yaml(data, output_path):
    """
    将数据写入到自定义格式的 .yaml 文件，前加 payload:
    :param data: list, 需要转换的原始数据
    :param output_path: str, 输出的 yaml 文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as yaml_file:
        yaml_file.write("payload:\n")  # 添加 payload
        for line in data:
            if line.startswith('#'):
                # 保留注释行
                yaml_file.write(line + "\n")
            elif line:  # 跳过空行
                # 添加两个空格和破折号
                yaml_file.write("  - " + line + "\n")
    print(f"已覆盖文件: {output_path}")

def convert_file_to_yaml(file_path):
    """
    将指定文件转换为 .yaml 文件
    :param file_path: str, 需要转换的文件路径
    """
    file_data = read_file(file_path)
    yaml_path = os.path.splitext(file_path)[0] + '.yaml'  # 直接使用相同的文件名
    write_custom_yaml(file_data, yaml_path)
    return yaml_path

def process_files(file_urls):
    """
    下载并处理文件
    :param file_urls: list, 文件的 URL 列表
    """
    for file_url in file_urls:
        file_name = file_url.split('/')[-1]

        # 下载文件，如果文件有更新则处理
        if download_file(file_url, file_name):
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
