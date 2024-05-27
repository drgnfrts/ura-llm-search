import os
import shutil
from bs4 import BeautifulSoup


# def convert_images_to_links(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')

#     for img in soup.find_all('img'):
#         try:
#             img_url = "https://ura.gov.sg" + img['data-original']
#             link = soup.new_tag('a', href=img_url)
#             link.string = img_url
#             img.replace_with(link)
#         except:
#             pass

#     return str(soup)


def fix_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # for link in soup.find_all('a', href=True):
    #     if link['href'].startswith('https://ura.gov.sg/'):
    #         link['href'] = link['href'].replace(
    #             'https://ura.gov.sg', 'https://www.ura.gov.sg')

    # Convert the soup object back to a string

    # return html_content.replace("https://ura.gov.sg", 'https://www.ura.gov.sg')

    for link in soup.find_all('a', href=True):
        if link['href'].startswith('/Corporate'):
            link['href'] = "https://www.ura.gov.sg" + link['href']
    return str(soup)


def process_html_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    modified_html = fix_links(html_content)

    temp_file_path = input_path + '.tmp'
    with open(temp_file_path, 'w', encoding='utf-8') as file:
        file.write(modified_html)

    shutil.move(temp_file_path, input_path)


def process_directory(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.html'):
                input_file_path = os.path.join(root, file)
                process_html_file(input_file_path)


def main():
    input_dir = '../data/Development-Control'
    process_directory(input_dir)


if __name__ == "__main__":
    main()
