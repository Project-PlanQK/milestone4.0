# This is a Gradio chat interface that interacts with an Azure OpenAI model.
from http import client
import sys
import gradio as gr
import os
import time
from openai import AzureOpenAI
import openai
import asyncio
import json
from techy_mode import handle_techy
from business_mode import handle_business
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
#from dotenv import load_dotenv
from chat_history import ChatHistoryManager

# Try to import dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("Warning: python-dotenv not found, using environment variables directly")

# Near the top of your file, after imports

# Set environment variables directly if not present
if not os.environ.get("AZURE_OPENAI_API_KEY"):
    print("Setting API key directly in code")
    os.environ["AZURE_OPENAI_API_KEY"] = "xy"
    os.environ["SEARCH_KEY"] = "xy"
    os.environ["SEARCH_ENDPOINT"] = "xy"
    os.environ["DEPLOYMENT_NAME"] = "gpt-4o"
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "xy"

"""OpenTelemetry Configuration
This section configures OpenTelemetry for monitoring and telemetry collection."""
# Initialize OpenAI instrumentation for telemetry
OpenAIInstrumentor().instrument()

#initialize chat history manager
chat_manager = ChatHistoryManager()

tracer = trace.get_tracer(__name__)


print("Started script") #debug

# Define a function to post a request to the Azure OpenAI model
def post_request(messages):
    # Get environment variables for the configuration
    #endpoint = os.getenv("ENDPOINT_URL") #url of the Azure OpenAI endpoint #alt
    #endpoint="https://aifoundrydbe7986002173.services.ai.azure.com/models"
    #deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.environ.get("SEARCH_ENDPOINT") #url of the Azure Search endpoint
    search_key = os.environ.get("SEARCH_KEY") #using azure search key for the vector database (bot can search in the database)
    subscription_key = os.environ.get("AZURE_OPENAI_API_KEY") # Azure OpenAI API Key

    try:
        # Initialize Azure OpenAI Service client with key-based authentication
        # here a connection to the Azure OpenAI service is established
        client = AzureOpenAI(
            api_key=subscription_key,
            azure_endpoint="https://hhz-dbe-openai.openai.azure.com/",  # Nur Domain, ohne /openai/ #alt
            #azure_endpoint="https://aifoundrydbe7986002173.services.ai.azure.com",
            #api_version=api_version,
            api_version="2025-01-01-preview",
            #credential=DefaultAzureCredential(),
            #endpoint="https://aifoundrydbe7986002173.services.ai.azure.com/models",
        )
        #alt
        #connection_string = client.telemetry.get_connection_string()
        #configure_azure_monitor(connection_string=connection_string)
# Verbessere die Fehlerbehandlung für OpenTelemetry

        try:
            connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
            print(f"Application Insights Connection String available: {bool(connection_string)}")
            
            if connection_string and connection_string.strip():
                try:
                    configure_azure_monitor(connection_string=connection_string)
                    print("Azure Monitor configured successfully")
                except Exception as telemetry_error:
                    print(f"WARNING: Failed to configure Azure Monitor: {telemetry_error}")
                    # Weiter ausführen ohne Telemetrie
            else:
                print("WARNING: No Application Insights connection string found. Telemetry will not be sent.")
        except Exception as e:
            print(f"ERROR in OpenTelemetry setup: {e}")
        
        # Prepare the chat prompt by appending the user message to the conversation
        # change prompt based on the selected mode
        """if messages[0]["content"] == "Business Mode Activated.":
            messages = handle_business(messages)
        elif messages[0]["content"] == "Tech Mode Activated.":
            messages = handle_techy(messages)"""
        
        #Hi
        # Initialize the chat prompt with a system message
        # The system message sets the context for the conversation
        chat_prompt = [
            {
                "role": "system",
                "content": """
You are a helpful virtual assistant for the PlanQK platform (https://platform.planqk.de/home). Your job is to help users complete their tasks using only the retrieved context from PlanQK resources.

Guidelines:

Respond strictly based on the retrieved context. Do not use prior knowledge or assumptions.
If information is missing, ask focused follow-up questions.
Avoid restricted topics: politics, religion, legal/medical/financial advice, personal matters, or criticism.
Maintain a professional, concise, and friendly tone for a technical/business audience.
Vary your phrasing, even when using sample phrases.
Always end with: "Is there anything else I can help you with on PlanQK?"

Output Format:
Always include a final message to the user.
When presenting factual information based on retrieved content, include citations like "source: https://platform.planqk.de/quantum-backends'" directly after the statement as:
Single source: url
Multiple sources: url, url
Only provide information related to the PlanQK platform, its services, tools, documentation, or the user’s interactions with it. Do not answer questions beyond this scope.

Sample Phrases for Deflecting:

"I'm sorry, but I'm unable to discuss that topic. Is there something else I can help you with?"
"That's not something I can provide information on, but I'm happy to help with questions related to PlanQK."
Example Dialogue: User: We’re exploring AI for operational optimization. Can PlanQK support us? Assistant: Thanks for reaching out! PlanQK offers AI models and services for analytics and optimization. Could you share:

What kind of data you’re working with?
Are you evaluating or ready to deploy?
User: We have structured time-series data and want to explore. Assistant: Great. Check out:

Use Case: “Predictive Optimization for Dynamic Systems” UseCase_X
Model: “Generic AI Optimizer” AI_Opt_Model
Would you like help setting up a workspace or connecting data?

User: Yes, please. Assistant: Here's how to start:

Create a workspace under “Workspaces”.
Add the model via the “Services” tab.
Connect data via “Data Connectors”.
Run a test with sample data.
Is there anything else I can help you with on PlanQK? 


"""
            },
        ]
        
        # Add user messages to the conversation
        # Loop through the messages and append them to the chat prompt
        for message in messages:
            chat_prompt.append({
                "role": message["role"],
                "content": message["content"]
            })

        # Generate the completion from the OpenAI model
        # The model is specified as "gpt-4o" and the chat prompt is passed as input
        # The completion is generated using the chat prompt and the extra_body parameters
        # here the model is called
        # the models response behavior is controlled by the parameters:

        model_name = os.environ.get("DEPLOYMENT_NAME", "gpt-4o")
        completion = client.chat.completions.create(
            model=model_name,
            messages=chat_prompt,
            max_tokens=800, 
            temperature=0.7, # controls the randomness of the output (0.0 - 1.0)
            top_p=0.95, # controls the diversity of the output (0.0 - 1.0)
            frequency_penalty=0, # controls the repetition of words (0.0 - 1.0)
            presence_penalty=0, # controls the presence of new words (0.0 - 1.0)
            stop=None, # stop sequence for the generation (None means no stop sequence)
            stream=False, # whether to stream the response
            extra_body={ # additional parameters for the Azure Search
            "data_sources": [{  # specify data source type
                "type": "azure_search",
                "parameters": {
                "filter": None, # filter to limit the search results (e.g., "category eq 'news'")
                "endpoint": search_endpoint,
                "index_name": "rag-1749220504930",
                "semantic_configuration": "",
                "authentication": {
                    "type": "api_key",
                    "key": search_key
                },
                "query_type": "simple",
                "in_scope": False, #setting in_scope to false means, that documents not belonging to the database or topic will be used and searched additionally
                #"role_information": "You are an AI assistant that helps people find information.",
                "strictness": 1, # strictness of the search results (0-5). 0 means no strictness, 5 means very strict. The stricter the search, the more relevant the results are. The strictness has to be between 1 and 5, where 1 allows a greater variety in answers with more data being seen as possibly relevant
                "top_n_documents": 10 # number of documents to retrieve from the search (1-10). The more documents are retrieved, the more relevant the results are. The top_n_documents has to be between 1 and 10, where 1 means only one document is retrieved and 10 means all documents are retrieved.
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
    
def chatbot_interaction(user_message, history):

    try:
        result_generator = post_request(history)
        result = ""
        for partial in result_generator:
            result += partial  # get the result from the generator (can be multiple times
        history.append({"role": "assistant", "content": result})
        return history, result
    
    except Exception as e:
        error_msg = f"Error during OpenAI request: {e}"
        history.append({"role": "assistant", "content": error_msg})
        return history, ""
    
#for normal LLM
async def bot_simple(history, chat_id=None):
    try:
        bot_response = post_request(history)
        history.append({"role": "assistant", "content": bot_response})
        # Save the updated history
        if chat_id:
            chat_id = chat_manager.save_chat(history, chat_id)
        else:
            chat_id = chat_manager.save_chat(history)
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
    
    # Get updated chat list
    updated_choices = get_chat_history_list()
    return (
        history, 
        gr.update(interactive=True, value=""), 
        chat_id, 
        gr.update(choices=updated_choices, value=None)  # Reset dropdown value to None
    )

async def bot_with_thinking(user_message, history, chat_id=None):
    if not user_message.strip():
        history.append({"role": "assistant", "content": "Please type a message first!"})
        updated_choices = get_chat_history_list()
        yield (
            history, 
            gr.update(value="", interactive=True), 
            chat_id, 
            gr.update(choices=updated_choices, value=None)
        )
        return
    
    history.append({"role": "user", "content": user_message})

    #thinking llm
    thinking_base = "Thinking..."
    for i in range(1, 4):
        await asyncio.sleep(0.5)
        history.append({"role": "assistant", "content": thinking_base + "." * i})
        updated_choices = get_chat_history_list()
        yield (
            history, 
            gr.update(interactive=False), 
            chat_id, 
            gr.update(choices=updated_choices, value=None)
        )
        history.pop()

    thinking_phrases = [
        "First, I need to understand the core aspects of the query...",
        "Now, considering the broader context and implications...",
        "Analyzing potential approaches to formulate a comprehensive answer...",
        "Finally, structuring the response for clarity and completeness..."
    ]
    
    updated_choices = get_chat_history_list()
    yield (
        history, 
        gr.update(interactive=False), 
        chat_id, 
        gr.update(choices=updated_choices, value=None)
    )
    
    # Show thinking phrases
    for phrase in thinking_phrases:
        await asyncio.sleep(0.5)
        history.append({"role": "assistant", "content": phrase})
        updated_choices = get_chat_history_list()
        yield (
            history, 
            gr.update(interactive=False), 
            chat_id, 
            gr.update(choices=updated_choices, value=None)
        )

    # Remove thinking messages
    history = [msg for msg in history if not any(p in msg["content"] for p in thinking_phrases)]

    # Get real response
    try:
        bot_response = post_request(history)
        history.append({"role": "assistant", "content": bot_response})
        if chat_id:
            chat_id = chat_manager.save_chat(history, chat_id)
        else:
            chat_id = chat_manager.save_chat(history)
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
    
    updated_choices = get_chat_history_list()
    yield (
        history, 
        gr.update(value="", interactive=True), 
        chat_id, 
        gr.update(choices=updated_choices, value=None)
    )
    
    #if user sends  a message, append it to the history and show it in the chat
def user(user_message, history):
    history.append({"role": "user", "content": user_message})
    return "", history
    #return "", history + [{"role": "user", "content": user_message}]

def like(evt: gr.LikeData):
    print("User liked the response")
    print(evt.index, evt.liked, evt.value)

def start_new_chat():
    """Starts a new chat with the initial greeting message"""
    return initial_greeting

def load_chat_history(chat_id):
    history = chat_manager.load_chat(chat_id)
    if history:
        return history
    return initial_greeting

def get_chat_history_list():
    try:
        chats = chat_manager.get_chat_list()
        print(f"Available chats: {len(chats)}")  # Debug print
        # Format for dropdown: [(label, value), ...]
        formatted_chats = [(f"{chat['preview']} ({chat['timestamp'][:10]})", chat['id']) for chat in chats]
        print(f"Formatted chats: {formatted_chats}")  # Debug print
        return formatted_chats
    except Exception as e:
        print(f"Error getting chat history list: {e}")
        return []

initial_greeting = [{"role": "assistant", "content": "Hello and welcome to PlanQK! I'm your virtual assistant and here to help you with:\n    •\tAnswering your questions about the PlanQK platform\n    •\tIdentifying suitable algorithms or use cases for your technical or business challenges\n    •\tSupporting the implementation of use cases based on your specific requirements\n    How may I assist you?\n"}]

#old - "Hey! I am a Chatbot and I'm here to assist you! Please select a mode first. You can choose between Business and Techy mode."
#add custom CSS styles to the Gradio app
with open("styles.css") as styles:
    styles_css = styles.read()

# Create a Gradio chat interface
with gr.Blocks(css=styles_css) as demo:
    gr.Markdown("<h2 style='text-align: center;'>PlanQK Assistant</h2>")
    
    # Add a State for the current chat ID
    current_chat_id = gr.State(value=None)
    
    with gr.Row():
        with gr.Column(scale=3):
            # Initialize dropdown with better error handling
            try:
                initial_choices = get_chat_history_list()
            except Exception as e:
                print(f"Error getting initial chat history: {e}")
                initial_choices = []
            
            chat_history_dropdown = gr.Dropdown(
                choices=initial_choices,
                label="Previous Conversations",
                interactive=True,
                value=None,
                multiselect=False
            )
        with gr.Column(scale=1):
            new_chat_button = gr.Button("New Chat", elem_classes="blue-button")
    
    chatbot = gr.Chatbot(value=initial_greeting, type="messages", height=500, show_copy_button=True)
    state = gr.State(value=initial_greeting)

    with gr.Row():
        business_button = gr.Button("Business", elem_classes="blue-button")
        techy_button = gr.Button("Techy", elem_classes="blue-button")
        delete_chat_button = gr.Button("Delete Chat", elem_classes="red-button")
    
    selected_mode = gr.State(value="")

    # Handle mode button clicks
    business_button.click(
        fn=lambda history: history + [{"role": "assistant", "content": "Business Mode Activated."}],
        inputs=chatbot, 
        outputs=chatbot
    )
    
    techy_button.click(
        fn=lambda history: history + [{"role": "assistant", "content": "Tech Mode Activated."}],
        inputs=chatbot, 
        outputs=chatbot
    )
    
    # New chat function - simplified
    def reset_chat():
        return initial_greeting, None
    
    new_chat_button.click(
        reset_chat,
        inputs=None,
        outputs=[chatbot, current_chat_id]
    )

    def load_selected_chat(selected_value):
        print(f"Loading chat with ID: {selected_value}")  # Debug print
        if selected_value:
            try:
                loaded_history = load_chat_history(selected_value)
                print(f"Loaded history length: {len(loaded_history) if loaded_history else 0}")  # Debug print
                return loaded_history, selected_value
            except Exception as e:
                print(f"Error loading chat {selected_value}: {e}")
                return initial_greeting, None
        return initial_greeting, None
    
    def update_dropdown():
        try:
            choices = get_chat_history_list()
            print(f"Updating dropdown with choices: {choices}")  # Debug print
            return gr.update(choices=choices, value=None)  # Always reset value to None
        except Exception as e:
            print(f"Error updating dropdown: {e}")
            return gr.update(choices=[], value=None)
    
    chat_history_dropdown.change(
        fn=load_selected_chat,
        inputs=[chat_history_dropdown],
        outputs=[chatbot, current_chat_id]
    )
    
    # Delete chat function
    def delete_current_chat(chat_id):
        if chat_id:
            chat_manager.delete_chat(chat_id)
        return None, initial_greeting
    
    delete_chat_button.click(
        delete_current_chat,
        inputs=[current_chat_id],
        outputs=[current_chat_id, chatbot]
    )

    with gr.Row():
        with gr.Column(scale=6):
            msg = gr.Textbox(label="Message", scale=3)
        with gr.Column(scale=2):
            thinking_button = gr.Button("Thinking LLM", elem_classes="pink-button")
            clear_button = gr.Button("Clear", elem_classes="pink-button")

    def debug_chat_manager():
        print("=== Chat Manager Debug ===")
        chats = chat_manager.get_chat_list()
        print(f"Total chats: {len(chats)}")
        for chat in chats:
            print(f"Chat ID: {chat['id']}, Preview: {chat['preview']}")
        print("========================")

    # Call this function after creating a new chat to verify it's being saved
    def debug_save_chat(history, chat_id=None):
        if chat_id:
            result_id = chat_manager.save_chat(history, chat_id)
        else:
            result_id = chat_manager.save_chat(history)
        debug_chat_manager()
        return result_id

    # Simplified bot functions - remove dropdown updates from here
    async def bot_simple_fixed(history, chat_id=None):
        try:
            bot_response = post_request(history)
            history.append({"role": "assistant", "content": bot_response})
            if chat_id:
                chat_id = debug_save_chat(history, chat_id)  # Use debug version
            else:
                chat_id = debug_save_chat(history)  # Use debug version
        except Exception as e:
            history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        
        return history, gr.update(interactive=True, value=""), chat_id

    async def bot_with_thinking_fixed(user_message, history, chat_id=None):
        if not user_message.strip():
            history.append({"role": "assistant", "content": "Please type a message first!"})
            yield history, gr.update(value="", interactive=True), chat_id
            return
        
        history.append({"role": "user", "content": user_message})

        # Thinking animation
        thinking_base = "Thinking..."
        for i in range(1, 4):
            await asyncio.sleep(0.5)
            history.append({"role": "assistant", "content": thinking_base + "." * i})
            yield history, gr.update(interactive=False), chat_id
            history.pop()

        thinking_phrases = [
            "First, I need to understand the core aspects of the query...",
            "Now, considering the broader context and implications...",
            "Analyzing potential approaches to formulate a comprehensive answer...",
            "Finally, structuring the response for clarity and completeness..."
        ]
        
        yield history, gr.update(interactive=False), chat_id
        
        # Show thinking phrases
        for phrase in thinking_phrases:
            await asyncio.sleep(0.5)
            history.append({"role": "assistant", "content": phrase})
            yield history, gr.update(interactive=False), chat_id

        # Remove thinking messages
        history = [msg for msg in history if not any(p in msg["content"] for p in thinking_phrases)]

        # Get real response
        try:
            bot_response = post_request(history)
            history.append({"role": "assistant", "content": bot_response})
            if chat_id:
                chat_id = chat_manager.save_chat(history, chat_id)
            else:
                chat_id = chat_manager.save_chat(history)
        except Exception as e:
            history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        
        yield history, gr.update(value="", interactive=True), chat_id

    # Function to update dropdown separately
    def update_dropdown():
        return gr.update(choices=get_chat_history_list())

    # Button handlers - separate dropdown updates
    thinking_button.click(
        bot_with_thinking_fixed, 
        inputs=[msg, chatbot, current_chat_id], 
        outputs=[chatbot, msg, current_chat_id]
    ).then(
        update_dropdown,
        inputs=None,
        outputs=[chat_history_dropdown]
    )
   
    # Message submit handler
    msg.submit(
        user, 
        inputs=[msg, chatbot], 
        outputs=[msg, chatbot], 
        queue=False
    ).then(
        bot_simple_fixed, 
        inputs=[chatbot, current_chat_id], 
        outputs=[chatbot, msg, current_chat_id]
    ).then(
        update_dropdown,
        inputs=None,
        outputs=[chat_history_dropdown]
    )

    # Clear and delete button handlers
    clear_button.click(lambda: None, None, chatbot, queue=False)
    
    delete_chat_button.click(
        delete_current_chat,
        inputs=[current_chat_id],
        outputs=[current_chat_id, chatbot]
    ).then(
        update_dropdown,
        inputs=None,
        outputs=[chat_history_dropdown]
    )
    
    new_chat_button.click(
        reset_chat,
        inputs=None,
        outputs=[chatbot, current_chat_id]
    ).then(
        update_dropdown,
        inputs=None,
        outputs=[chat_history_dropdown]
    )

    chatbot.like(like)

# Launch the app
port = int(os.environ.get("PORT", 8080))
demo.launch(show_error=True, server_name="0.0.0.0", server_port=port)