import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
                if line not in seen_lines:  # Remove duplicates
                    seen_lines.add(line)
                    merged_lines.append(line)
    
    return merged_lines

def write_custom_yaml(data, output_path):
    """
    Write data to a custom formatted .yaml file with an entry count comment.
    :param data: list, content to write
    :param output_path: str, file path for the output yaml file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as yaml_file:
            yaml_file.write(f"# Total entries: {len(data)}\n")
            yaml_file.write("payload:\n")
            for line in data:
                if line.startswith('#'):
                    yaml_file.write(line + "\n")
                elif line:
                    yaml_file.write("  - " + line + "\n")
        logging.info(f"YAML file written: {output_path}")
    except IOError as e:
        logging.error(f"Failed to write YAML file {output_path}: {e}")

def process_file(file_name, urls):
    """
    Download, merge contents, and generate YAML file.
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

    # Create directory named after the file (without extension)
    folder_name = os.path.splitext(file_name)[0]
    os.makedirs(folder_name, exist_ok=True)

    # Write merged content to YAML file
    yaml_path = os.path.join(folder_name, os.path.splitext(file_name)[0] + '.yaml')
    write_custom_yaml(merged_content, yaml_path)

    # Write merged content to plain text file
    list_file_path = os.path.join(folder_name, file_name)
    try:
        with open(list_file_path, 'w', encoding='utf-8') as list_file:
            list_file.write("\n".join(merged_content))
        logging.info(f"Merged file saved: {list_file_path}")
    except IOError as e:
        logging.error(f"Failed to write merged file {list_file_path}: {e}")

if __name__ == "__main__":
    # Define the files to download and their respective URLs
    file_map = {
        "DownloadCDN_CN.list": [
            "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/DownloadCDN_CN.list"
        ],
        "Emby.list": [
            "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/Emby.list
            "https://raw.githubusercontent.com/kirito12827/kk_zawuku/refs/heads/clash/rule/emby.list"
        ],
        "Talkatone.list": [
            "https://raw.githubusercontent.com/Repcz/Tool/refs/heads/X/Clash/Rules/Talkatone.list"
        ]
    }

    # Process each file
    for file_name, urls in file_map.items():
        process_file(file_name, urls)
