import os
import csv
import time
import json
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def create_directory_structure(base_dir, url, start_from):
    '''
    This is a helper function to create a local directory structure that mimics the site hierarchy, using the path segments (e.g. each / will create a new subdirectory)

    Parameters:
        base_dir (string): Relative link to the directory that the subdirectories of HTMLs will be stored in
        url (string): URA webpage URL
        start_from (string): Specific path segment in the URL to start the hierarchical directory structure creation from

    Returns:
        full_path (string): Full local directory path of where the HTML resource will be stored in

    '''
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL")

        start_index = parsed_url.path.find(start_from)
        if start_index == -1:
            raise ValueError(
                f"The start_from segment '{start_from}' not found in the URL path")

        relevant_path = parsed_url.path[start_index:].lstrip('/')
        parent_dir = os.path.dirname(relevant_path)
        full_path = os.path.join(base_dir, parent_dir)
        # DELETE THIS SEGMENT
        try:
            os.makedirs(full_path, exist_ok=True)
        except:
            pass
        return full_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def convert_images_to_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for img in soup.find_all('img'):
        try:
            img_url = "https://www.ura.gov.sg" + img['data-original']
            link = soup.new_tag('a', href=img_url)
            link.string = img_url
            img.replace_with(link)
        except:
            pass

    return str(soup)


def scrape_and_save_csv(csv_file, base_dir, start_from):
    '''
    This is the main function to scrape the DC guidelines from the URA website into local HTML files in a manner that mimics the site hierarchy, with Selenium. Scraping cannot be run headless due to webpage restrictions.

    Parameters:
        csv_file (csv): File of URA weblinks to parse through
        base_dir (string):  Relative link to the directory that the subdirectories of HTMLs will be stored in
        start_from (string): Specific path segment in the URL to start the hierarchical directory structure creation from

    '''
    errors_dict = {}

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url = row[0]
                if "https://www.ura.gov.sg/-/media/Corporate/Guidelines/Development-control" in url:
                    print(f"Media file: {url} - skipping...")
                    continue

                print(f"Processing URL: {url}")
                directory = create_directory_structure(
                    base_dir, url, start_from)
                if directory is None:
                    print(f"Failed to create directory for URL: {url}")
                    continue

                driver.get(url)
                errors = []
                content_html_1 = content_html_2 = content_html_3 = ""

                try:
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#pnlMain > div.fullbody-wrapper.no-t-padding > div > div.row > div.col-sm-9.col-md-9.col-xs-12')))
                except:
                    errors.append("Main header wait condition failed")
                    print("Main header wait condition failed")

                try:
                    content_html_1 = driver.find_element(
                        By.CSS_SELECTOR, '#pnlMain > div.fullbody-wrapper.no-t-padding > div > div.row > div.col-sm-9.col-md-9.col-xs-12 > div'
                    ).get_attribute("outerHTML")
                except:
                    errors.append("Main header not found")
                    print("Main header not found")

                try:
                    content_html_2 = driver.find_element(
                        By.CSS_SELECTOR, '#pnlMain > div.fullbody-wrapper.no-t-padding > div > div.row > div.col-sm-9.col-md-9.col-xs-12 > div.fullbody-wrapper.no-t-padding > div > div > div'
                    ).get_attribute("outerHTML")
                except:
                    errors.append("Main body not found")
                    print("Main body not found")

                try:
                    content_html_3 = driver.find_element(
                        By.CSS_SELECTOR, '#pnlMain > div.fullbody-wrapper.no-t-padding > div > div.row > div.col-sm-9.col-md-9.col-xs-12 > div:nth-child(5)'
                    ).get_attribute("outerHTML")
                except:
                    try:
                        content_html_3 = driver.find_element(
                            By.CSS_SELECTOR, '#pnlMain > div.fullbody-wrapper.no-t-padding > div > div.row > div.col-sm-9.col-md-9.col-xs-12 > div:nth-child(3)'
                        ).get_attribute("outerHTML")
                    except:
                        errors.append("Date not found")
                        print("Date not found")

                html_content = convert_images_to_links(
                    content_html_1 + content_html_2 + content_html_3)

                if not html_content.strip():
                    errors.append("No content found")
                    print("No content found, skipping URL...")
                    continue

                if errors:
                    errors_dict[url] = errors

                parsed_url = urlparse(url)

                filename = os.path.basename(parsed_url.path)
                if not filename.endswith('.html'):
                    filename += '.html'
                file_path = os.path.join(directory, filename)

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_content)

                print(f"Saved content of URL: {url} to {file_path}")
                time.sleep(0.25)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    with open("../data/errors.json", "w") as outfile:
        json.dump(errors_dict, outfile)


def main():
    csv_file = '../data/dc_links.csv'
    base_dir = '../data'
    start_from = 'Development-Control'
    scrape_and_save_csv(csv_file, base_dir, start_from)


if __name__ == "__main__":
    main()
