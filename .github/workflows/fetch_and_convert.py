import os
import requests
import shutil
import hashlib
import subprocess

def download_file(file_url, save_path):
    """
    下载文件并验证是否有变化。
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

def process_file_content(file_path):
    """
    处理 .list 文件内容，转换为 .yaml 格式
    :param file_path: str, 需要处理的文件路径
    :return: str, 处理后的文件路径
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    processed_content = []
    for line in content:
        line = line.strip()
        if line and not line.startswith("#"):  # 排除空行和注释行
            processed_content.append(f"  - {line}")
    
    # 写入新的文件
    new_file_path = file_path.replace('.list', '.yaml')
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write("payload:\n")
        for line in processed_content:
            new_file.write(line + "\n")
    
    return new_file_path

def git_commit_and_push():
    """
    检查并提交本地更改到 Git 仓库
    """
    try:
        # 检查 Git 仓库状态
        git_status = subprocess.check_output(["git", "status", "-s"]).decode("utf-8")
        if git_status:
            subprocess.check_call(["git", "config", "--local", "user.email", "your-email@example.com"])
            subprocess.check_call(["git", "config", "--local", "user.name", "Your Name"])
            subprocess.check_call(["git", "add", "-A"])
            commit_message = "Auto Update " + subprocess.check_output("date +'%Y-%m-%d %H:%M:%S'", shell=True).decode("utf-8").strip()
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "origin", "main"])  # 请根据分支调整 "main"
            print("更新已提交并推送到仓库.")
        else:
            print("没有更改需要提交.")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作失败: {e}")

def update_and_process_files(file_urls):
    """
    下载并处理文件，如果文件有更新则执行处理
    :param file_urls: list, 需要下载的文件URL
    """
    for file_url in file_urls:
        file_name = file_url.split('/')[-1]
        
        if download_file(file_url, file_name):
            folder_name = os.path.splitext(file_name)[0]
            os.makedirs(folder_name, exist_ok=True)
            shutil.move(file_name, os.path.join(folder_name, file_name))
            
            # 处理文件内容
            new_file_path = process_file_content(os.path.join(folder_name, file_name))
            shutil.move(new_file_path, os.path.join(folder_name, os.path.basename(new_file_path)))

def cleanup_files():
    """
    清理不需要的文件，保持仓库整洁
    """
    print("清理临时文件...")
    for temp_file in os.listdir("."):
        if temp_file.endswith(".list") or temp_file.endswith(".yaml"):
            os.remove(temp_file)

if __name__ == "__main__":
    # 定义要下载的多个文件的URL列表
    file_urls = [
        "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/DownloadCDN_CN.list",
        "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/Emby.list",
        "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/Talkatone.list"
    ]
    
    update_and_process_files(file_urls)
    git_commit_and_push()
    cleanup_files()
