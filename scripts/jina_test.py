import requests
from markdown_cleaner import MarkdownCleaner

jina = ""
url = "https://www.ura.gov.sg/Corporate/Guidelines/Development-Control/Non-Residential/B2/Allowable-Uses"
headers = {
    "X-Return-Format": "markdown",
    "X-Target-Selector": "#pnlMain",
    "X-Wait-For-Selector": "#pnlMain",
    "X-No-Cache": "true",
    # "Accept": "text/event-stream"

}

response = requests.get("https://r.jina.ai/" + url, headers=headers)

if response.status_code == 200:
    jina = response.text
    # print(jina)
else:
    print(f"Request failed with status code: {response.status_code}")


# content = jina[jina.find('"content"') + 11:jina.rfind("}")]
cleaner = MarkdownCleaner(jina, url)
results = cleaner.clean()
with open("../docs/test2.md", "w") as file:
    file.write(results)
