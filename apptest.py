# This is a Gradio chat interface that interacts with an Azure OpenAI model.
import gradio as gr
import os
import time
from openai import AzureOpenAI
import openai
import asyncio
import json

print("Skript startet")
# Define a function to post a request to the Azure OpenAI model
def post_request(messages):
    # Get environment variables for the configuration
    #endpoint = os.getenv("ENDPOINT_URL")  # Azure OpenAI endpoint
    #subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  # Azure API Key
    #api_version = os.getenv("AZURE_API_VERSION")  # API Version
    #search_endpoint = os.getenv("SEARCH_ENDPOINT")
    #search_key = os.getenv("SEARCH_KEY")

    endpoint = os.getenv("ENDPOINT_URL")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_key = os.getenv("SEARCH_KEY")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    try:
        # Initialize Azure OpenAI Service client with key-based authentication
        #from transformers_js_py import AzureOpenAI  # Import AzureOpenAI from transformers_js_py
        client = AzureOpenAI(
            api_key=subscription_key,
            azure_endpoint=endpoint,  # Nur Domain, ohne /openai/
            #api_version=api_version,
            api_version="2025-01-01-preview",
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
            model="gpt-4o",
            #model=os.getenv("AZURE_DEPLOYMENT_NAME"),
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
                "in_scope": False, #setting in_scope to false means, that documents not belonging to the database will be used and searched additionally
                #"role_information": "You are an AI assistant that helps people find information.",
                "strictness": 1, #strictness has to be between 1 and 5, where 1 allows a greater variety in answers with more data being seen as possibly relevant
                "top_n_documents": 5
                }
            }]
            }
        )
        
        # Extract and return the model's response
        #result = completion.choices[0].message['content']
        result = completion.choices[0].message.content
        return result

    except Exception as e:
        # Handle any exceptions that occur during the request
        raise gr.Error(f"An error occurred: {str(e)}")
    
def simulate_thinking_chat(message):
    thoughts = [
        "First, I need to understand the core aspects of the query...",
        "Now, considering the broader context and implications...",
        "Analyzing potential approaches to formulate a comprehensive answer...",
        "Finally, structuring the response for clarity and completeness..."
    ]
    answer = ""
    
    # Denken simulieren und Fortschritt anzeigen
    for thought in thoughts:
        time.sleep(0.5)  # Pausen für die Simulation von "Denken"
        answer += f"- {thought}\n"
        yield answer.strip()  # Streaming-Ausgabe (stufenweise)

def chatbot_interaction(user_message, history):
    #history.append({"role": "user", "content": user_message})
    # Die eigentliche Anfrage an den Chatbot erfolgt hier
    # Beispiel einer Dummy-Antwort für den Chatbot
    #response = f"Bot: I received your message: '{user_message}'. How can I assist you further?"
    #result = completion.choices[0].message.content
    
    #history.append({"role": "user", "content": user_message})
    #history.append({"role": "assistant", "content": result})
    
    #return history, result

    try:
        result_generator = post_request(history)
        result = ""
        for partial in result_generator:
            result += partial  # Hol dir das Ergebnis aus dem Generator (auch mehrfach möglich)

        history.append({"role": "assistant", "content": result})
        return history, result
    except Exception as e:
        error_msg = f"Error during OpenAI request: {e}"
        history.append({"role": "assistant", "content": error_msg})
        return history, ""

# Create a Gradio chat interface
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    #output_box = gr.Textbox(label="Thinking output", lines=10, interactive=False)
    msg = gr.Textbox(label="Message")
    clear = gr.Button("Clear")
    
    # Button, der die 'simulate_thinking_chat' Funktion auslöst
    #button = gr.Button("Thinking LLM")
    #button.click(fn=simulate_thinking_chat, inputs=msg, outputs=output_box)

    def user(user_message, history):
        return "", history + [{"role": "user", "content": user_message}]

    #def bot(history):
        #bot_message = post_request(history)
        #history.append({"role": "assistant", "content": bot_message})
        #return history

    async def bot_with_thinking(history):
        thinking_phrases = [
            "First, I need to understand the core aspects of the query...",
            "Now, considering the broader context and implications...",
            "Analyzing potential approaches to formulate a comprehensive answer...",
            "Finally, structuring the response for clarity and completeness..."
        ]

        # Zeige Thinking-Phrasen nacheinander
        for phrase in thinking_phrases:
            await asyncio.sleep(0.5)
            history.append({"role": "assistant", "content": phrase})
            yield history

        # Entferne Thinking-Nachrichten, um nur die finale Antwort zu zeigen (optional)
        history = [msg for msg in history if not any(p in msg["content"] for p in thinking_phrases)]

        # Danach kommt der echte Bot-Output
        try:
            bot_response = post_request(history)
            history.append({"role": "assistant", "content": bot_response})
        except Exception as e:
            history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        
        yield history


    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_with_thinking, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the Gradio app
port = int(os.environ.get("PORT", 8080))  # fallback
demo.launch(show_error=True, server_name="0.0.0.0", server_port=port)