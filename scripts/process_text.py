'''
Supersedes data_extraction.ipynb. To be readapted for use in pipeline later.
'''


from unstructured.partition.html import partition_html
from openai import OpenAI


def get_body(elements):
    '''
    This function finds the document element list indexes corresponding to the main body of the webpage, in the absence of usage of proper body tags

    Parameters:
        elements (list): A list of Unstructured document objects

    Returns:
        list: The sliced elements list whose indexes point to document objects containing text and other metadata from the main body of the webpage
    '''

    START = 0
    END = 0
    flag = False

    for i in range(len(elements)):

        if flag == False and elements[i].text == 'Earthworks, Retaining Walls, and Boundary Walls':
            flag = True
            continue
        elif START == 0 and elements[i].category == 'Title' and flag == True:
            START = i
            continue
        elif END == 0 and elements[i].text == 'Urban Redevelopment Authority' and flag == True:
            END = i
            break
    return elements[START:END]


def html_to_markdown(input_html, output_file_path):
    '''
    This function extracts the text from the main body of the webpage and and passes it into the GPT4-o API to be chunked and sent to markdown format. Remember to set your OpenAI API key in environment variables before running.

    Parameters:
        input_html (string): URL of the webpage desired
        output_file_path (string): Relative path to directory to store .md files

    Returns:
        None
    '''

    elements = partition_html(url=input_html,
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})

    body_elements = get_body(elements)
    text = str()
    for item in body_elements:
        text += item.text + " "

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "I want you to be an expert in processing text into chunks for natural language processing . I am building a vector database of text and I have a document in a string. I want you to chunk the document into appropriate paragraph, creating headers by re-using the text inside the paragraphs where possible. Do not add anything to the paragraphs that is outside the string, and do not re-seqeunce the text, only chunk it. Return only these chunked paragraphs in Markdown with h2 headers for each chunk without any pre-empted welcome or response message."
             },
            {"role": "user",
             "content": f"The text is as follows: {text}"}
        ]
    )

    completion_text = completion.choices[0].message.content
    print(completion_text)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(completion_text)
    print("Completion result saved to", output_file_path)


def main():
    html_to_markdown(
        "https://www.ura.gov.sg/Corporate/Guidelines/Development-Control/Non-Residential/Transport/RC-Flat-Roofs", "../docs/RC.mdx")


if __name__ == "__main__":
    main()
