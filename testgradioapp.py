# This is a Gradio chat interface that interacts with an Azure OpenAI model.
import gradio as gr
import os
from openai import OpenAI
import openai
import asyncio
import json


# Define a function to post a request to the Azure OpenAI model
def post_request(messages):
    # Get environment variables for the configuration
    endpoint = os.getenv("ENDPOINT_URL")  # Azure OpenAI endpoint
    deployment = os.getenv("DEPLOYMENT_NAME")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  # Azure API Key
    api_version = os.getenv("AZURE_API_VERSION")  # API Version
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_key = os.getenv("SEARCH_KEY")

    openai.api_type = "azure" 
    openai.api_version = api_version
    openai.api_base = f"https://{endpoint}.openai.azure.com/"
    openai.api_key = subscription_key
 
    try:
        # Initialize Azure OpenAI Service client with key-based authentication
        #from transformers_js_py import AzureOpenAI  # Import AzureOpenAI from transformers_js_py
        client = openai.OpenAI(
            api_key=subscription_key,
            #api_version="2024-11-20",
        )
        
        # Prepare the chat prompt by appending the user message to the conversation
        chat_prompt = [
            {
                "role": "system",
                "content": "You are an AI assistant that helps people find information."
            },
        ]
        
        # Add user messages to the conversation
        for message in messages:
            chat_prompt.append({
                "role": message["role"],
                "content": message["content"]
            })

        # Generate the completion from the OpenAI model
        completion = client.chat.completions.create(
            #engine="gpt-4o-mini",
            model=deployment,
            messages=chat_prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
            extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                "filter": None,
                "endpoint": search_endpoint,
                "index_name": "hhz-ds-test-index",
                "semantic_configuration": "",
                "authentication": {
                    "type": "api_key",
                    "key": search_key
                },
                "query_type": "simple",
                "in_scope": True,
                "role_information": "You are an AI assistant that helps people find information.",
                "strictness": 3,
                "top_n_documents": 5
                }
            }]
            }
        )
        
        # Extract and return the model's response
        result = completion.choices[0].message['content']
        return result

    except Exception as e:
        # Handle any exceptions that occur during the request
        raise gr.Error(f"An error occurred: {str(e)}")

# Create a Gradio chat interface
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(label="Message")
    clear = gr.Button("Clear")

    def user(user_message, history):
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history):
        bot_message = post_request(history)
        history.append({"role": "assistant", "content": bot_message})
        return history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the Gradio app
port = int(os.environ.get("PORT", 8080))  # fallback
demo.launch(show_error=True, server_name="0.0.0.0", server_port=port)