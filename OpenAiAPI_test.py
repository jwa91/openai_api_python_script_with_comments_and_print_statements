import openai
import gradio as gr
import os
import time

# Load API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")

print("API Key loaded.")

# Instantiate the OpenAI client
client = openai.OpenAI(api_key=api_key)
print("OpenAI client instantiated.")

# ID of your existing assistant
assistant_id = "asst_key_that_you_have_to_create"  # Replace with your assistant's ID
print(f"Using Assistant ID: {assistant_id}")

thread_id = None

def custom_chatgpt(user_input, session_state=None):
    global thread_id  # Use the global thread ID

    if session_state is None:
        session_state = []

    if thread_id is None:
        print("Creating a new thread...")
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"Thread created with ID: {thread_id}")
    else:
        print(f"Using existing thread with ID: {thread_id}")

    # Create a new message in the thread
    print("Sending user input to the thread...")
    client.beta.threads.messages.create(
        thread_id=thread_id,  # Use thread_id directly
        role="user",
        content=user_input
    )
    print("User input sent.")

    # Create and execute a run using the existing assistant
    print("Creating and executing a run...")
    run = client.beta.threads.runs.create(
        thread_id=thread_id,  # Use thread_id directly
        assistant_id=assistant_id,
    )
    print("Run created.")

    # Check the status of the assistant
    while True:
        print("Checking run status...")
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)  # Use thread_id directly
        print(f"Run status: {run.status}")

        if run.status == "completed":
            print("Run completed. Retrieving messages...")
            messages = client.beta.threads.messages.list(thread_id=thread_id)  # Use thread_id directly

            chatgpt_reply = ""
            if messages:
                for message in messages:
                    print(f"Message found: {message}")
                    if message.role == "assistant":
                        chatgpt_reply += message.content[0].text.value + "\n"
                        print(f"Assistant message added to reply: {message.content[0].text.value}")
            else:
                print("No messages found.")

            break
        else:
            print("Run still in progress, waiting for 5 seconds...")
            time.sleep(5)

    return chatgpt_reply, session_state

# Gradio Interface
demo = gr.Interface(
    fn=custom_chatgpt,
    inputs=[gr.Textbox(label="ask question"), gr.State()],
    outputs=[gr.Textbox(label="answer"), gr.State()],
    title="Test interface",
    description="description"
)

print("Launching Gradio interface...")
demo.launch(share=True)
