import re
from markdownify import markdownify as md
import json


class MarkdownCleaner:
    """
    Contains the necessary functions used to extract the semi-clean Jira.AI API scrape of the URA website for ChatDCG Indexing
    """

    def __init__(self, api_response, url, date_pattern):
        """
        Initialise MarkdownCleaner for the given API response and URL.

        Parameters:
            markdown_content (str): Raw markdown content from the Jira.AI API scrape.
            URL (str): URL of the URA webpage.
        """
        self.url = url
        self.title = ''
        self.date = 'No date found'
        self.cleaned_markdown = ''
        self.header = ''
        self.content = api_response
        self.date_pattern = date_pattern

    def process_top_text_header(self, markdown):
        """
        Finds the header, removes any and all text above it, and stores the header and title for processing in the next function. This should always work because every webpage has a heading...right?
        """
        header_match = re.search(r'^(#{1,3} .+)$', markdown, re.MULTILINE)
        if not header_match:
            first_line_match = re.search(r'^(.+)$', markdown, re.MULTILINE)
            if first_line_match:
                header_match = first_line_match
        markdown = markdown[header_match.start():]
        self.header = header_match.group(1)

        return markdown

    def insert_metadata(self, markdown):
        """
        Extracts the updated date from page, reformats the header to h2, and adds the metadata below the header in a YAML format as such:

            ## header
            ---
            title: title
            link: url
            date: last updated date
            ---
        """
        self.title = self.header.strip('#').strip()
        date_match = re.search(self.date_pattern, markdown)
        # date_match = re.search(
        #     r'(Last updated on|Published:) (.+(19|20)\d{2})', markdown)
        if date_match and self.date_pattern != '':
            print("DATE FOUND")
            self.date = date_match.group(1).strip("_").strip()

        yaml_metadata = f"\n---\ntitle: {self.title}\n\nlink: {self.url}\n\ndate: {self.date}\n\n---\n"

        new_header = "## " + self.title + yaml_metadata

        return markdown.replace(self.header, new_header, 1)

    def strip_stars_lines(self, markdown):
        """
        Removes lines containing only * * * from the Markdown.
        """
        return re.sub(r'^\* \* \*$', '', markdown, flags=re.MULTILINE)

    def remove_italics(self, markdown):
        """
        Remove italics without affecting underscores in links
        """
        return re.sub(r'(\s|^)_(.+)_', r'\1', markdown, flags=re.MULTILINE)

    def process_bullet_points(self, markdown):
        """
        Converts bullet points from * to -
        """
        return re.sub(r'^\* ', r'- ', markdown, flags=re.MULTILINE)

    def remove_weird_chars(self, markdown):
        """
        Removes all the weird characters that are going to affect my UTF-8 writing to Markdown file
        """
        replacements = {
            '‘': "'",
            '’': "'",
            '“': '"',
            '”': '"',
            "≤": "<=",
            "≥": ">=",
            "×": "*",
            "&nbsp;": " ",
            "•": "-",
        }

        for char, replacement in replacements.items():
            markdown = markdown.replace(char, replacement)
        return markdown

    def remove_internal_links(self, markdown):
        """
        Removes only internal page references and converts them to normal text (either header or plain text)

            Before: [#### Smaller Header](#Smaller Header)
            After: #### Smaller Header
        """
        return re.sub(r'\[(.+?)\]\(#.+?\)', r'\1', markdown, flags=re.MULTILINE)

    def convert_links(self, html):
        """
        Converts links from HTML format into Markdown format, and adds https://ura.gov.sg to local links.
        """
        html = re.sub(
            r'(<a href=")(?!https:\/\/|http:\/\/)([^"]+).+>(.+)(<\/a>)', r'<a href="https://www.ura.gov.sg\2">\3<\/a>', html)
        # Below to add to web links
        html = re.sub(r'\[([^]]+)\]\((?!https://|http://)([^)]+)\)',
                      r'[\1](https://www.ura.gov.sg\2)', html)
        # Below to add to embedded image links for rendering
        html = re.sub(r'!\[([^]]*)\]\((?!https://)([^)]+)\)',
                      r'![\1](https://www.ura.gov.sg\2)', html)
        return html

    def clean(self):
        """
        Main function to be called externally for cleaning of Markdown content. Function calls sequence as such:

        Returns:
            markdown (str): Final cleaned Markdown content
        """
        markdown = self.process_top_text_header(self.content)
        markdown = self.insert_metadata(markdown)
        markdown = self.strip_stars_lines(markdown)
        markdown = self.remove_italics(markdown)
        markdown = self.process_bullet_points(markdown)
        markdown = self.remove_weird_chars(markdown)
        markdown = self.remove_internal_links(markdown)
        markdown = self.convert_links(markdown)

        return markdown
