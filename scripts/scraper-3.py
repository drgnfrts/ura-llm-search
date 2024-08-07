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


def generate_cleaned_md(url, date_pattern):
    """
    Fetch the markdown content and clean it using the MarkdownCleaner class.
    """
    jina = ""
    headers = {
        "X-Return-Format": "markdown",
        "X-Target-Selector": "#pnlMain",
        "X-Wait-For-Selector": "##pnlMain > div:nth-child(7) > div > div > div > div.text-cms-col > div:nth-child(1) > a",
        "X-No-Cache": "true",
    }
    while jina == "":
        response = requests.get("https://r.jina.ai/" + url, headers=headers)
        jina = response.text
        time.sleep(3)
    cleaner = MarkdownCleaner(jina, url, date_pattern)
    results = cleaner.clean()
    return results


def process_csv(csv_file, base_dir, start_from, date_pattern):
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            url = row[0]
            if "https://www.ura.gov.sg/-/media/" in url:
                print(f"Media file: {url} - skipping...")
                continue
            print(f"Processing URL: {url}")

            # Create the directory structure
            directory = create_directory_structure(base_dir, url, start_from)
            if directory is None:
                print(f"Failed to create directory for URL: {url}")
                continue
#
            cleaned_results = generate_cleaned_md(url, date_pattern)
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith('.md'):
                filename += '.md'
            file_path = os.path.join(directory, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_results)


if __name__ == "__main__":

    csv_config = {
        'Development-Control.csv': {
            'start_from': 'Development-Control',
            'date_pattern': r'Last updated on (.+(19|20)\d{2})'
        },
        'Circulars.csv': {
            'start_from': 'Circulars',
            'date_pattern': r'Published (.+(19|20)\d{2})'
        },
        'Media-Releases.csv': {
            'start_from': 'Media-Room',
            'date_pattern': r'Published (.+(19|20)\d{2})'
        },
        'Forum-Replies.csv': {
            'start_from': 'Media-Room',
            'date_pattern': r'reply, (.+(19|20)\d{2})'
        },
        # 'Home-Business.csv': {
        #     'start_from': 'Home-Business',
        #     'date_pattern': ''
        # },
        'Property.csv': {
            'start_from': 'Property',
            'date_pattern': ''
        },
    }

    csv_files = [
        # '../data/Development-Control.csv',
        # '../data/Circulars.csv',
        # '../data/Media-Releases.csv',
        # '../data/Forum-Replies.csv',
        '../data/Property.csv',
        # '../data/Home-Business.csv',
    ]

    base_dir = '../data/chat-ura'

    for csv_file in csv_files:
        # Extract the base name of the CSV file to use as a key in the dictionary
        csv_name = os.path.basename(csv_file)
        if csv_name in csv_config:
            config = csv_config[csv_name]
            start_from = config['start_from']
            date_pattern = config['date_pattern']
            print(date_pattern)
            process_csv(csv_file, base_dir, start_from, date_pattern)
