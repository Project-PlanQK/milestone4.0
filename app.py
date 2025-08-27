# This is a Gradio chat interface that interacts with an Azure OpenAI model.
import gradio as gr
import os
import time
from openai import AzureOpenAI
import openai
import asyncio
import json
from techy_mode import handle_techy
from business_mode import handle_business
# Import necessary libraries for OpenTelemetry
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from user_profile import UserProfile

"""OpenTelemetry Configuration
This section configures OpenTelemetry for monitoring and telemetry collection."""
# Initialize OpenAI instrumentation for telemetry
OpenAIInstrumentor().instrument()

tracer = trace.get_tracer(__name__)

print("Skript startet") #debug

# Define a function to post a request to the Azure OpenAI model
def post_request(messages, user_profile=None):
    # Get environment variables for the configuration
    # Get environment variables for the configuration
    endpoint = os.getenv("ENDPOINT_URL") #url of the Azure OpenAI endpoint #alt
    #endpoint="https://aifoundrydbe7986002173.services.ai.azure.com/models"
    #deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.getenv("SEARCH_ENDPOINT") #url of the Azure Search endpoint
    search_key = os.getenv("SEARCH_KEY") #using azure search key for the vector database (bot can search in the database)
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY") # Azure OpenAI API Key
        
    try:
        # Initialize Azure OpenAI Service client with key-based authentication
        # here a connection to the Azure OpenAI service is established
        client = AzureOpenAI(
            api_key=subscription_key,
            azure_endpoint=endpoint,  # Nur Domain, ohne /openai/ #alt
            #azure_endpoint="https://aifoundrydbe7986002173.services.ai.azure.com/models",
            #api_version=api_version,
            api_version="2025-01-01-preview",
            #credential=DefaultAzureCredential(),
            #endpoint="https://aifoundrydbe7986002173.services.ai.azure.com/models",
        )
        #alt
        #connection_string = client.telemetry.get_connection_string()
        #configure_azure_monitor(connection_string=connection_string)
        connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        print(f"Application Insights Connection String available: {bool(connection_string)}")
        if connection_string:
            configure_azure_monitor(connection_string=connection_string)
            print("Azure Monitor configured successfully")
        else:
            print("WARNING: No Application Insights connection string found. Telemetry will not be sent.")
        
        # Prepare the chat prompt by appending the user message to the conversation
        # change prompt based on the selected mode
        """if messages[0]["content"] == "Business Mode Activated.":
            messages = handle_business(messages)
        elif messages[0]["content"] == "Tech Mode Activated.":
            messages = handle_techy(messages)"""
    except Exception as e:
        print(f"Error initializing Azure OpenAI client or configuring telemetry: {e}")
        raise

            # Only call user profile LLM if not set
    if user_profile is None:
        with tracer.start_as_current_span("User-Profiling") as span:
            user_profiler = UserProfile()
            # Only pass the latest user message
            last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            user_profile = user_profiler.determine_user_profile(last_user_message)
            span.set_attribute("user.profile", user_profile)

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
                At the end of each response, explicitly state which persona you have identified (Identified persona: Business | Technical).

                Output Format:
                Always include a final message to the user.
                When presenting factual information based on retrieved content, include citations like "source: https://platform.planqk.de/quantum-backends'" directly after the statement as:
                Single source: url
                Multiple sources: url, url
                Only provide information related to the PlanQK platform, its services, tools, documentation, or the user’s interactions with it. Do not answer questions beyond this scope.

                Sample Phrases for Deflecting:

                "I'm sorry, but I'm unable to discuss that topic. Is there something else I can help you with?"
                "That's not something I can provide information on, but I'm happy to help with questions related to PlanQK."
                Example Dialogue: User: We're exploring AI for operational optimization. Can PlanQK support us? Assistant: Thanks for reaching out! PlanQK offers AI models and services for analytics and optimization. Could you share:

                What kind of data you're working with?
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
                Identified User Profile: {user_profile}"""
            },
        ]
        
        # Add user messages to the conversation
        # Loop through the messages and append them to the chat prompt
        for message in messages:
            chat_prompt.append({
                "role": message["role"],
                "content": message["content"]
            })

        # Main LLM Call
        with tracer.start_as_current_span("RAG-Context-Retrieval") as span:
            # Set attributes for the span to provide additional context
            span.set_attribute("rag.index_name", "rag-1749220504930")
            span.set_attribute("rag.top_n_documents", 10)
            span.set_attribute("rag.strictness", 1)
            span.set_attribute("rag.query_type", "simple")
            span.set_attribute("rag.in_scope", False)

            # Generate the completion from the OpenAI model within a new span
        with tracer.start_as_current_span("Model-Completion") as span:
            try:
                client = AzureOpenAI(
                    api_key=subscription_key,
                    azure_endpoint=endpoint,
                    api_version="2025-01-01-preview",
                )
                completion = client.chat.completions.create(
                    model="gpt-4o",
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

                # Citations / Dokumente
                citations = getattr(completion.choices[0], "citations", None)
                span.set_attribute("rag.documents_used", bool(citations))
                if citations:
                    span.set_attribute("rag.num_documents", len(citations))
                    for i, doc in enumerate(citations):
                        span.set_attribute(f"rag.doc_{i}.url", doc.get("url", ""))
                        span.set_attribute(f"rag.doc_{i}.title", doc.get("title", ""))
                        span.set_attribute(f"rag.doc_{i}.chunk_index", doc.get("chunk_index", -1))

                # Modell-Infos
                span.set_attribute("model.finish_reason", completion.choices[0].finish_reason)
                span.set_attribute("model.response_length", len(completion.choices[0].message.content))
                span.set_attribute("model.total_tokens", completion.usage.total_tokens)

                # Extract and return the model's response
                result = completion.choices[0].message.content
                return result

            except Exception as e:
                # Handle any exceptions that occur during the request
                raise gr.Error(f"An error occurred: {str(e)}")
    
def chatbot_interaction(user_message, history, user_profile):
    try:
        result_generator = post_request(history, user_profile)
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
async def bot_simple(history, user_profile):
    try:
        bot_response = post_request(history, user_profile)
        history.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
    return history, user_profile, gr.update(interactive=True, value="")

#for thinking LLM
async def bot_with_thinking(user_message, history, user_profile):
    if not user_message.strip():
        # if no message is entered
        history.append({"role": "assistant", "content": "Please type a message first!"})
        yield history, user_profile, gr.update(value="", interactive=True)
        return
    history.append({"role": "user", "content": user_message})
    #yield history, gr.update(value="", interactive=False)

    thinking_base = "Thinking..."
    for i in range(1, 4):  # three steps: ., .., ...
        await asyncio.sleep(0.5)
        history.append({"role": "assistant", "content": thinking_base + "." * i})
        yield history, gr.update(interactive=False)
        history.pop()

    thinking_phrases = [
        "First, I need to understand the core aspects of the query...",
        "Now, considering the broader context and implications...",
        "Analyzing potential approaches to formulate a comprehensive answer...",
        "Finally, structuring the response for clarity and completeness..."
        ]
    yield history, gr.update(interactive=False)
    
    # show thinking phrases in the chat
    for phrase in thinking_phrases:
        await asyncio.sleep(0.5)
        history.append({"role": "assistant", "content": phrase})
        yield history, user_profile, gr.update(interactive=False)  # Update the chatbot with the thinking phrase

    # remove thinking messages from history to show only the final answer
    history = [msg for msg in history if not any(p in msg["content"] for p in thinking_phrases)]

    #Bot-Output, get real response from OpenAI
    try:
        bot_response = post_request(history, user_profile)
        history.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})

    yield history, user_profile, gr.update(value="", interactive=True)  # Update the chatbot with the final response ## Clear the message box after sending

    #if user sends  a message, append it to the history and show it in the chat
def user(user_message, history):
    history.append({"role": "user", "content": user_message})
    return "", history
    #return "", history + [{"role": "user", "content": user_message}]

"""def like(evt: gr.LikeData):
    print("User liked the response")
    print(evt.index, evt.liked, evt.value)"""

def like(evt: gr.LikeData, history, user_profile):
    if evt.liked:
        # Thumbs up: thank the user
        history.append({"role": "assistant", "content": "Thanks for your feedback!"})
        return history, user_profile
    else:
        # Thumbs down: ask for a more detailed answer
        last_user_message = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        # Add a special system prompt for more detail
        system_prompt = (
            "The user requested a more detailed answer. "
            "Please provide a more comprehensive and in-depth response to the last user question."
        )
        temp_history = history.copy()
        temp_history.append({"role": "system", "content": system_prompt})
        try:
            bot_response = post_request(temp_history, user_profile)
            history.append({"role": "assistant", "content": bot_response})
        except Exception as e:
            history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        return history, user_profile

def copy_last_message(history):
    if history:
        return history[-1]["content"]
    return ""

initial_greeting = [{"role": "assistant", "content": "Hello and welcome to PlanQK! I'm your virtual assistant and here to help you with:\n    •\tAnswering your questions about the PlanQK platform\n    •\tIdentifying suitable algorithms or use cases for your technical or business challenges\n    •\tSupporting the implementation of use cases based on your specific requirements\n    How may I assist you?\n"}]

#old - "Hey! I am a Chatbot and I'm here to assist you! Please select a mode first. You can choose between Business and Techy mode."
#add custom CSS styles to the Gradio app
with open("styles.css") as styles:
    styles_css = styles.read()

# Create a Gradio chat interface
with gr.Blocks(css=styles_css) as demo:
    gr.Markdown("<h2 style='text-align: center;'>Helping Chatbot</h2>")
    chatbot = gr.Chatbot(value=initial_greeting, type="messages")
    user_profile_state = gr.State(value=None)

    with gr.Row():
        copy_button = gr.Button("Copy Last Message")
        copy_output = gr.Textbox(label="Copied Text", interactive=False)

    copy_button.click(copy_last_message, inputs=chatbot, outputs=copy_output)

    with gr.Row():
        with gr.Column(scale=6):
            msg = gr.Textbox(label="Message", scale=3)  # left side, larger space
        with gr.Column(scale=2):  # right side, smaller space
            thinking_button = gr.Button("Thinking LLM", elem_classes="blue-button") #make button blue
            clear_button = gr.Button("Clear", elem_classes="blue-button") #make button blue

    #handle the thinking button click
    thinking_button.click(bot_with_thinking, inputs=[msg, chatbot, user_profile_state], outputs=[chatbot, user_profile_state, msg])#.then(bot_with_thinking, inputs=chatbot, outputs=[chatbot, msg])
    #thinking_button.click(bot_with_thinking, inputs=chatbot, outputs=[chatbot, msg])
   
    #handle textbox submit
        #invoke the user function and update the textbox and chat history
        #then call the bot_with_thinking function to get the response from the bot
    msg.submit(user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
        bot_simple, inputs=[chatbot, user_profile_state], outputs=[chatbot, user_profile_state, msg]
    )

    # clear button to clear the chat history
    clear_button.click(lambda: (initial_greeting, None), None, [chatbot, user_profile_state], queue=False)
    #chatbot.like(like)
    chatbot.like(
    like,
    inputs=[chatbot, user_profile_state],
    outputs=[chatbot, user_profile_state]
    )

# Launch the Gradio app
port = int(os.environ.get("PORT", 8080))  # fallback 7860
demo.launch(show_error=True, server_name="0.0.0.0", server_port=port)
