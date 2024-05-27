import os
import shutil
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.environ.get("URA_OPENAI_API_KEY"))

# Retrieve the assistant and vector store details once
assistant = client.beta.assistants.retrieve(
    assistant_id=os.environ.get("URA_MARKDOWN_ASSISTANT_ID"))
vector_store = client.beta.vector_stores.retrieve(
    vector_store_id=os.environ.get("URA_MARKDOWN_CLEANER_VECTOR_STORE_ID"))

# Update the assistant with the vector store information
client.beta.assistants.update(
    model="gpt-3.5-turbo",
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    temperature=0.05
)


def process_markdown_file(md_file_path, markdown_file_path):
    """Process a single markdown file by sending its contents to the OpenAI API."""
    # Upload the markdown file to be accessible by the API
    if os.path.exists(markdown_file_path):
        return 1
    with open(md_file_path, "rb") as file:
        file = client.files.create(file=file, purpose="assistants")

    # Create a thread for processing
    thread = client.beta.threads.create()
    thread_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Return the Markdown and links in-line. Take note of any rowspan or colspan in tables. Do not give any welcome or ending message, only the Markdown output. If the page is extremely short, no need for h2 headers, just return the h1 header and normal text. ",
        attachments=[{"file_id": file.id, "tools": [{"type": "file_search"}]}]
    )

    class EventHandler(AssistantEventHandler):
        @override
        def on_message_done(self, message) -> None:
            # Logic to handle the completion of a message
            # This should be implemented based on the specific details of the response
            message_content = message.content[0].text
            with open(markdown_file_path, 'w', encoding='utf-8') as f:
                f.write(f"{message_content.value}\n")

    # Listen to the thread and process events
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    # Clean up: delete the message and the uploaded file
    client.beta.threads.messages.delete(
        message_id=thread_message.id, thread_id=thread.id)
    client.files.delete(file.id)


def copy_directory_structure_only(src, dest):
    """Copies only the directory structure from src to dest."""
    # Ensure the base destination directory exists
    if not os.path.exists(dest):
        os.makedirs(dest)

    for root, dirs, files in os.walk(src):
        # Calculate the relative path from the source directory to the current directory
        rel_path = os.path.relpath(root, src)
        # Construct the corresponding path in the destination
        dest_path = os.path.join(dest, rel_path)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)


if __name__ == "__main__":
    original_dir = '..\\data\\Development-Control-md'
    new_dir = '..\\data\\DC-cleaned-md'

    # Copy directory structure without files
    copy_directory_structure_only(original_dir, new_dir)

    # Process each Markdown file
    for root, dirs, files in os.walk(original_dir):
        for name in files:
            if name.endswith('.md'):
                old_md_path = os.path.join(root, name)
                new_md_path = old_md_path.replace(original_dir, new_dir)
                try:
                    task = process_markdown_file(old_md_path, new_md_path)
                    if task == 1:
                        print(f"Skipped API call: {new_md_path}")
                    else:
                        print(f"Successfully cleaned to {new_md_path}")
                except Exception as e:
                    print(f"Failed to clean to {new_md_path}")
                    print(e.message, e.args)
