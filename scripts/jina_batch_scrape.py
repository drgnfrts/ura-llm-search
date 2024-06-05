import os
import csv
import time
from urllib.parse import urlparse
from markdown_cleaner import MarkdownCleaner
import requests


def create_directory_structure(base_dir, url, start_from):
    """
    Create a directory structure based on the URL, starting from a specified part of the URL path,
    excluding the base directory and network location. Creates directories up to the parent of the last segment.
    """
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL")

        # Find the starting index of the desired directory structure
        start_index = parsed_url.path.find(start_from)
        if start_index == -1:
            raise ValueError(
                f"The start_from segment '{start_from}' not found in the URL path")

        # Extract the relevant path starting from the specified part
        relevant_path = parsed_url.path[start_index:].lstrip('/')

        # Get the parent directory of the last segment
        parent_dir = os.path.dirname(relevant_path)

        # Construct the full path to the parent directory
        full_path = os.path.join(base_dir, parent_dir)

        # Create directories if they do not exist
        if not os.path.exists(full_path):
            os.makedirs(full_path)

        return full_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def generate_cleaned_md(url):
    jina = ""
    headers = {
        "X-Return-Format": "markdown",
        "X-Target-Selector": "#pnlMain",
        "X-Wait-For-Selector": "#pnlMain",
        "X-No-Cache": "true",
        # "Accept": "text/event-stream"
    }
    while jina == "":
        response = requests.get("https://r.jina.ai/" + url, headers=headers)
        jina = response.text
        time.sleep(3)
    cleaner = MarkdownCleaner(jina, url)
    results = cleaner.clean()
    return results


csv_file = '../data/dc_links.csv'
base_dir = '../data'
start_from = 'Development-Control'

with open(csv_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url = row[0]
        if "https://www.ura.gov.sg/-/media/Corporate/Guidelines/Development-control" in url:
            print(f"Media file: {url} - skipping...")
            continue
        print(f"Processing URL: {url}")

        # Create the directory structure
        directory = create_directory_structure(base_dir, url, start_from)
        if directory is None:
            print(f"Failed to create directory for URL: {url}")
            continue
        cleaned_results = generate_cleaned_md(url)
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename.endswith('.md'):
            filename += '.md'
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_results)
