import os
import re
import time


def extract_date(content):
    """Extracts the text starting from 'Last updated on' to the specified year '2024', inclusively."""
    # Regex to capture everything from "Last updated on" to "2024"
    pattern = r".*Last updated on(.*\d{4}).*"
    match = re.search(pattern, content)
    try:
        date_string = match.group(1).replace('*', '')
    except:
        date_string = 'No date found'
    content = re.sub(pattern, '', content)
    return date_string, content


def format_link(file_path):
    """Formats the link based on the file path."""
    base_url = 'https://www.ura.gov.sg/Corporate/Guidelines/Development-Control'
    relative_path = file_path.split(
        'DC-cleaned-md')[-1].replace('\\', '/').lstrip('/').replace('.md', '')
    return f'{base_url}/{relative_path}'


def add_yaml_metadata(file_path):
    """Reads file, extracts required info, and writes back with YAML metadata."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Assumes the first line is the title

    title = content.splitlines()[0].lstrip('#').strip()
    link = format_link(file_path)
    date, content = extract_date(content)
    date = date.strip()

    # Create YAML metadata
    yaml_metadata = f"---\ntitle: {title}\nlink: {link}\ndate: {date}\n---\n\n"

    # Write back to file with YAML metadata prepended
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(yaml_metadata + content)


def process_directory(directory):
    """Walks through the directory and processes each Markdown file."""
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith('.md'):
                file_path = os.path.join(root, name)
                add_yaml_metadata(file_path)


if __name__ == "__main__":
    # directory = '../data/DC-cleaned-md'
    # process_directory(directory)
    add_yaml_metadata(
        "..\\data\\DC-cleaned-md\\gross-floor-area\\GFA\\CoveredWalkwayandLinkages.md")
