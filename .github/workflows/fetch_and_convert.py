import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define rule types in the order of priority
RULE_ORDER = [
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "IP-CIDR",
    "IP-CIDR6",
    "IP-SUFFIX"
]

def download_file(file_url):
    """
    Download the specified file.
    :param file_url: str, URL of the file
    :return: str, content of the downloaded file
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logging.info(f"File downloaded from: {file_url}")
        return response.text  # Return file content
    except requests.RequestException as e:
        logging.error(f"Failed to download {file_url}: {e}")
        return None

def merge_file_contents(file_contents):
    """
    Merge file contents, removing duplicates and preserving order.
    :param file_contents: list, content of each file
    :return: list, merged content
    """
    merged_lines = []
    seen_lines = set()

    for content in file_contents:
        if content:
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line not in seen_lines:  # Remove duplicates and comments
                    seen_lines.add(line)
                    merged_lines.append(line)
    
    return merged_lines

def sort_rules(rules):
    """
    Sort rules based on RULE_ORDER and alphabetically.
    :param rules: list, list of rule strings
    :return: list, sorted rules
    """
    def rule_key(line):
        parts = line.split(",")
        if parts[0] in RULE_ORDER:
            return (RULE_ORDER.index(parts[0]), parts[1])  # Sort by rule type and alphabetically
        else:
            return (len(RULE_ORDER), line)  # Unknown types go to the end

    return sorted(rules, key=rule_key)

def format_to_payload(file_name, content):
    """
    Format content into the required payload format.
    :param file_name: str, name of the .list file
    :param content: list, cleaned and sorted content of the file
    """
    folder_name = os.path.splitext(file_name)[0]
    os.makedirs(folder_name, exist_ok=True)

    list_file_path = os.path.join(folder_name, file_name)
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # Remove extension

    # Prepare content with payload format
    formatted_content = [
        "payload:",
        f"# 规则名称: {rule_name}",
        f"# 规则数量: {rule_count}"
    ] + [f"  - {line}" for line in content]

    # Write to file
    try:
        with open(list_file_path, 'w', encoding='utf-8') as list_file:
            list_file.write("\n".join(formatted_content))
        logging.info(f"Formatted file saved: {list_file_path}")
    except IOError as e:
        logging.error(f"Failed to write formatted file {list_file_path}: {e}")

def process_file(file_name, urls):
    """
    Download, merge contents, sort rules, and generate formatted .list file.
    :param file_name: str, name of the file
    :param urls: list, list of URLs to download the file from
    """
    file_contents = []
    for url in urls:
        content = download_file(url)
        if content is not None:
            file_contents.append(content)
    
    # Merge contents
    merged_content = merge_file_contents(file_contents)

    # Sort rules
    sorted_content = sort_rules(merged_content)

    # Format content and save to file
    format_to_payload(file_name, sorted_content)

if __name__ == "__main__":
    # Define the files to download and their respective URLs
    file_map = {
        "DownloadCDN_CN.list": [
            "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/DownloadCDN_CN.list"
        ],
        "Emby.list": [
            "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/Emby.list",
            "https://raw.githubusercontent.com/kirito12827/kk_zawuku/refs/heads/clash/rule/emby.list"
        ],
        "Talkatone.list": [
            "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/Talkatone.list"
        ]
    }

    # Process each file
    for file_name, urls in file_map.items():
        process_file(file_name, urls)
