import os
import requests
import logging
import json
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 定义规则类型的排序优先级
RULE_ORDER = [
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "IP-CIDR",
    "IP-CIDR6",
    "IP-SUFFIX",
]


def download_file(file_url: str) -> Optional[str]:
    """
    下载指定文件。
    :param file_url: 文件的 URL
    :return: 文件内容（字符串），失败时返回 None
    """
    try:
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()  # 抛出 HTTP 错误
        logging.info(f"文件下载成功: {file_url}")
        return response.text
    except requests.RequestException as e:
        logging.error(f"文件下载失败: {file_url} - {e}")
        return None


def merge_file_contents(file_contents: List[str]) -> List[str]:
    """
    合并文件内容，去除重复项和注释行。
    :param file_contents: 文件内容列表
    :return: 合并后的内容列表
    """
    merged_lines = []
    seen_lines = set()

    for content in file_contents:
        if content:
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line not in seen_lines:
                    seen_lines.add(line)
                    merged_lines.append(line)

    return merged_lines


def sort_rules(rules: List[str]) -> List[str]:
    """
    根据规则类型和字母顺序对规则进行排序。
    :param rules: 规则列表
    :return: 排序后的规则列表
    """

    def rule_key(line: str) -> tuple:
        parts = line.split(",")
        if parts[0] in RULE_ORDER:
            return (RULE_ORDER.index(parts[0]), parts[1])
        return (len(RULE_ORDER), line)

    return sorted(rules, key=rule_key)


def write_list_file(file_name: str, content: List[str]) -> None:
    """
    将内容写入 .list 文件，并添加标题注释。
    :param file_name: 文件名
    :param content: 内容列表
    """
    folder_name = os.path.splitext(file_name)[0]
    folder_path = os.path.join("rule", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    list_file_path = os.path.join(folder_path, file_name)
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]

    # 添加标题注释
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则数量: {rule_count}",
    ] + content

    try:
        with open(list_file_path, "w", encoding="utf-8") as list_file:
            list_file.write("\n".join(formatted_content))
        logging.info(f".list 文件保存成功: {list_file_path}")
    except IOError as e:
        logging.error(f".list 文件保存失败: {list_file_path} - {e}")


def write_yaml_file(file_name: str, content: List[str]) -> None:
    """
    将内容写入 YAML 文件，并添加 payload 格式。
    :param file_name: 文件名
    :param content: 内容列表
    """
    folder_name = os.path.splitext(file_name)[0]
    folder_path = os.path.join("rule", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    yaml_file_path = os.path.join(folder_path, f"{os.path.splitext(file_name)[0]}.yaml")
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]

    # 添加 payload 格式
    formatted_content = [
        "payload:",
        f"# 规则名称: {rule_name}",
        f"# 规则数量: {rule_count}",
    ] + [f"  - {line}" for line in content]

    try:
        with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write("\n".join(formatted_content))
        logging.info(f".yaml 文件保存成功: {yaml_file_path}")
    except IOError as e:
        logging.error(f".yaml 文件保存失败: {yaml_file_path} - {e}")


def process_file(file_name: str, urls: List[str]) -> None:
    """
    下载文件、合并内容、排序规则并生成 .list 和 .yaml 文件。
    :param file_name: 文件名
    :param urls: 文件的 URL 列表
    """
    file_contents = []
    for url in urls:
        content = download_file(url)
        if content is not None:
            file_contents.append(content)

    # 合并内容
    merged_content = merge_file_contents(file_contents)

    # 排序规则
    sorted_content = sort_rules(merged_content)

    # 写入 .list 和 .yaml 文件
    write_list_file(file_name, sorted_content)
    write_yaml_file(file_name, sorted_content)


if __name__ == "__main__":
    # 从 JSON 文件加载下载链接
    json_file_path = os.path.join(os.path.dirname(__file__), 'rule_list.json')
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        file_map = json.load(json_file)

    # 处理每个文件
    for file_name, urls in file_map.items():
        process_file(file_name, urls)