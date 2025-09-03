# mapping This is a Gradio chat interface that interacts with an Azure OpenAI model.
from urllib import response
import gradio as gr
import os
import time
from openai import AzureOpenAI
import openai
import asyncio
import json
import re
from techy_mode import handle_techy
from business_mode import handle_business
# Import necessary libraries for OpenTelemetry
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from user_profile import UserProfile
import gradio as gr

#gr.Chatbot.postprocess = False  # Disable default postprocessing

"""OpenTelemetry Configuration
This section configures OpenTelemetry for monitoring and telemetry collection."""
# Initialize OpenAI instrumentation for telemetry
OpenAIInstrumentor().instrument()

tracer = trace.get_tracer(__name__)

print("Starting post_request") #debug

# Define a function to post a request to the Azure OpenAI model
async def post_request(messages, user_profile=None):
    # Get environment variables for the configuration
    endpoint = os.getenv("ENDPOINT_URL") #url of the Azure OpenAI endpoint #alt
    #endpoint="https://aifoundrydbe7986002173.services.ai.azure.com/models"
    #deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.getenv("SEARCH_ENDPOINT") #url of the Azure Search endpoint
    search_key = os.getenv("SEARCH_KEY") #using azure search key for the vector database (bot can search in the database)
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY") # Azure OpenAI API Key

    # Determine user profile only once per session (or cache as needed)
    user_profiler = UserProfile()
    last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    if user_profile is None:
        user_profile = user_profiler.determine_user_profile(last_user_message)
    
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
                "At the end of each response, explicitly state which user profile you have identified (Identified User Profile: {user_profile})."                

                Output Format:
                Always include a final message to the user.
                When presenting factual information based on retrieved content, include citations like "source: https://platform.planqk.de/quantum-backends'" directly after the statement as:
                Single source: url
                Multiple sources: url, url
                Only provide information related to the PlanQK platform, its services, tools, documentation, or the user's interactions with it. Do not answer questions beyond this scope.

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
                Is there anything else I can help you with on PlanQK?"""
            },
        ]
        
        # Add user messages to the conversation
        # Loop through the messages and append them to the chat prompt
    for message in messages:
        chat_prompt.append({
            "role": message["role"],
            "content": message["content"]
        })

    # Initialize history if not defined
    history = []
    # Add previous history if needed
    for msg in history:
        chat_prompt.append(msg)

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
            print("Creating completion")  # Debug print
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=chat_prompt,
                max_tokens=800,
                temperature=0.7,  # controls the randomness of the output (0.0 - 1.0)
                top_p=0.95,  # controls the diversity of the output (0.0 - 1.0)
                frequency_penalty=0,  # controls the repetition of words (0.0 - 1.0)
                presence_penalty=0,  # controls the presence of new words (0.0 - 1.0)
                stop=None,  # stop sequence for the generation (None means no stop sequence)
                stream=True,  # whether to stream the response
                extra_body={ # additional parameters for the Azure Search
                        "data_sources": [{  # specify data source type
                            "type": "azure_search",
                            "parameters": {
                                "filter": None, # filter to limit the search results (e.g., "category eq 'news'")
                                "endpoint": search_endpoint,
                                "index_name": "rag-1749220504930",
                                # Find this name in your Azure Search Index -> Semantic configurations. It cannot be empty.
                                "semantic_configuration": "rag-1749220504930-semantic-configuration",
                                "authentication": {
                                    "type": "api_key",
                                    "key": search_key
                                },
                                "query_type": "vector_simple_hybrid",
                                "embedding_dependency": {
                                    "type": "deployment_name",
                                    # This must be the exact "Deployment name" from Azure AI Studio's "Deployments" page.
                                    "deployment_name": "text-embedding-3-large" 
                                },
                                "in_scope": True, #setting in_scope to false means, that documents not belonging to the database or topic will be used and searched additionally
                                #"role_information": "You are an AI assistant that helps people find information.",
                                "strictness": 1, # strictness of the search results (0-5). 0 means no strictness, 5 means very strict. The stricter the search, the more relevant the results are. The strictness has to be between 1 and 5, where 1 allows a greater variety in answers with more data being seen as possibly relevant
                                "top_n_documents": 10, # number of documents to retrieve from the search (1-10). The more documents are retrieved, the more relevant the results are. The top_n_documents has to be between 1 and 10, where 1 means only one document is retrieved and 10 means all documents are retrieved.
                                "fields_mapping": {
                                    "content_fields": ["chunk"],
                                    "vector_fields": ["text_vector"],
                                    "title_field": "title",
                                    "url_field": "url",
                                }
                            }
                        }],
                    }
                )
            print("Completion created, starting Streaming")  # Debug print

            # Process the streaming response
            citations = []
            full_response = ""
            
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    
                    # Check for citation metadata
                    if delta.tool_calls:
                        tool_call = delta.tool_calls[0]
                        if tool_call.function.name == "retrieval":
                            tool_args = json.loads(tool_call.function.arguments)
                            citations.extend(tool_args.get("citations", []))
                            print(f"Found citations: {len(citations)}")

                    # Stream content
                    if delta.content:
                        content_chunk = delta.content
                        full_response += content_chunk
                        yield content_chunk, None # Yield content chunk for streaming display

            # After streaming, replace placeholders with citations
            if citations:
                for i, citation in enumerate(citations):
                    doc_id = f"[doc{i+1}]"
                    title = citation.get('title', 'source')
                    url = citation.get('url', '#')
                    replacement = f"[{title}]({url})"
                    full_response = full_response.replace(doc_id, replacement)
            
            # Final processed response
            yield None, full_response

        except Exception as e:
            # Handle any exceptions that occur during the request
            raise gr.Error(f"Error in post_request: {str(e)}")
    
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
        print("bot_simple started")  # Debug print
        bot_response = ""
        result_generator = post_request(history, user_profile)
        
        async for chunk, final_response in result_generator:
            if chunk:
                print(f"Received chunk: {chunk}")  # Debug print
                bot_response += chunk
            elif final_response:
                bot_response = final_response # Use the final processed response
        
        print(f"Final response: {bot_response}")  # Debug print
        
        if bot_response.strip():
            history.append({"role": "assistant", "content": bot_response})
        else:
            history.append({"role": "assistant", "content": "I apologize, but I couldn't generate a response. Please try again."})
        
        return history, user_profile, gr.update(value="", interactive=True)
        
    except Exception as e:
        print(f"Error in bot_simple: {str(e)}")  # Debug print
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        return history, user_profile, gr.update(value="", interactive=True)

#for streaming LLM
async def bot_with_streaming(user_message, history, user_profile):
    if not user_message or not user_message.strip():
        yield history, user_profile, gr.update(value="", interactive=True)
        return

    history.append({"role": "user", "content": user_message})
    current_response = ""
    
    try:
        async for delta, final_response in post_request(history, user_profile):
            if delta:
                current_response += delta
                history_with_stream = history + [{"role": "assistant", "content": current_response}]
                yield history_with_stream, user_profile, gr.update(interactive=False)
                await asyncio.sleep(0.01)  # Small delay for smoother streaming
            elif final_response:
                # Final update with processed citations
                final_history = history + [{"role": "assistant", "content": final_response}]
                yield final_history, user_profile, gr.update(value="", interactive=True)
                return # End of streaming

        # Fallback if stream ends without a final response (should not happen with new logic)
        final_history = history + [{"role": "assistant", "content": current_response}]
        yield final_history, user_profile, gr.update(value="", interactive=True)
    
    except Exception as e:
        print(f"Error in bot_with_streaming: {str(e)}")
        error_history = history + [{"role": "assistant", "content": f"Error: {str(e)}"}]
        yield error_history, user_profile, gr.update(value="", interactive=True)

    #if user sends  a message, append it to the history and show it in the chat
def user(user_message, history):
    history.append({"role": "user", "content": user_message})
    return "", history
    #return "", history + [{"role": "user", "content": user_message}]

def like(evt: gr.LikeData, history, user_profile):
    if evt.liked:
        history.append({"role": "assistant", "content": "Thanks for your feedback!"})
        return history, user_profile
    else:
        last_user_message = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        system_prompt = (
            "The user requested a more detailed answer. "
            "Please provide a more comprehensive and in-depth response to the last user question."
        )
        temp_history = history.copy()
        temp_history.append({"role": "system", "content": system_prompt})
        try:
            bot_response = ""
            # This part is non-streaming, so it needs to be adapted.
            # For simplicity, let's make it async and use the new post_request
            # This requires making `like` async, which Gradio supports.
            # However, to keep changes minimal, we'll do a blocking call.
            
            async def get_response():
                full_response = ""
                async for chunk, final in post_request(temp_history, user_profile):
                    if chunk:
                        full_response += chunk
                    elif final:
                        full_response = final
                return full_response

            bot_response = asyncio.run(get_response())
            history.append({"role": "assistant", "content": bot_response})
        except Exception as e:
            history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        return history, user_profile
    
async def ask_predefined_question(question, history, user_profile):
    try:
        print(f"Processing question: {question}")  # Debug print
        history.append({"role": "user", "content": question})
        bot_response = ""
            
        # Get the response chunks
        async for chunk, final_response in post_request(history, user_profile):
            if chunk:
                print(f"Received chunk: {chunk}")  # Debug print
                bot_response += chunk
            elif final_response:
                bot_response = final_response # Use the final processed response
            
        print(f"Final response: {bot_response}")  # Debug print
            
        if bot_response.strip():  # Check if we got a non-empty response
            history.append({"role": "assistant", "content": bot_response})
        else:
            history.append({"role": "assistant", "content": "I apologize, but I couldn't generate a response. Please try again."})
            
        return history, user_profile, gr.update(value="", interactive=True)
    except Exception as e:
        print(f"Error in ask_predefined_question: {str(e)}")  # Debug print
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        return history, user_profile, gr.update(value="", interactive=True)

#initial_greeting = [{"role": "assistant", "content": "Hello and welcome to PlanQK! I'm your virtual assistant and here to help you with:\n    •\tAnswering your questions about the PlanQK platform\n    •\tIdentifying suitable algorithms or use cases for your technical or business challenges\n    •\tSupporting the implementation of use cases based on your specific requirements\n    How may I assist you?\n"}]
initial_greeting = [
    {"role": "assistant", "content": "Hello and welcome to PlanQK! I'm your virtual assistant and here to help you with:\n    •\tAnswering your questions about the PlanQK platform\n    •\tIdentifying suitable algorithms or use cases for your technical or business challenges\n    •\tSupporting the implementation of use cases based on your specific requirements\n    How may I assist you?\n"}
]

#old - "Hey! I am a Chatbot and I'm here to assist you! Please select a mode first. You can choose between Business and Techy mode."
#add custom CSS styles to the Gradio app
with open("styles.css") as styles:
    styles_css = styles.read()

# Create a Gradio chat interface
with gr.Blocks(css=styles_css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(
                value="./assets/PlanQK_Logo.png",  # Use relative path with ./
                show_label=False,
                height=40,
                container=False,
                scale=1
            )
        with gr.Column(scale=4):
            gr.Markdown("# PlanQK Assistant Chatbot")

    chatbot = gr.Chatbot(
        value=initial_greeting,
        height=400,
        show_copy_button=True,
        type="messages"  # Add this line
    )
    user_profile_state = gr.State(value=None)

    # --- Inline Question Buttons ---
    with gr.Row(elem_classes="button-row"):
        question1_btn = gr.Button(
            "Generate Use Case",
            elem_id="inline-q1",
            elem_classes="lilac-button"
        )
        question2_btn = gr.Button(
            "PlanQK Use Cases Info",   
            elem_id="inline-q2",
            elem_classes="lilac-button"
        )
        question3_btn = gr.Button(
            "Use Algorithm APIs",
            elem_id="inline-q3",
            elem_classes="lilac-button"
        )

    with gr.Row():
        with gr.Column(scale=6):
            msg = gr.Textbox(label="Message", scale=3)
        with gr.Column(scale=2):
            simple_button = gr.Button("Simple LLM", elem_classes="blue-button")  # Add this line
            streaming_button = gr.Button("Streaming LLM", elem_classes="blue-button")
            clear_button = gr.Button("Clear", elem_classes="blue-button")

    # --- Button click handlers ---
    simple_button.click(
        fn=user,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=False
    ).success(
        fn=bot_simple,
        inputs=[chatbot, user_profile_state],
        outputs=[chatbot, user_profile_state, msg],
        queue=True
    )

    question1_btn.click(
        ask_predefined_question,
        inputs=[gr.State("Please tell me how to generate my first Use Case."), chatbot, user_profile_state],
        outputs=[chatbot, user_profile_state, msg],
        queue=True
    )
    question2_btn.click(
        ask_predefined_question,
        inputs=[gr.State("Please give me further information about PlanQK Use Cases"), chatbot, user_profile_state],
        outputs=[chatbot, user_profile_state, msg],
        queue=True
    )
    question3_btn.click(
        ask_predefined_question,
        inputs=[gr.State("How can I use an Algorithm API?"), chatbot, user_profile_state],
        outputs=[chatbot, user_profile_state, msg],
        queue=True
    )

    #handle the streaming button click
    msg.submit(
        fn=user,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        queue=False
    ).success(
        fn=bot_simple,  # Change this from bot_with_streaming to bot_simple
        inputs=[chatbot, user_profile_state],
        outputs=[chatbot, user_profile_state, msg],
        queue=True
    )

    streaming_button.click(
        fn=bot_with_streaming,
        inputs=[msg, chatbot, user_profile_state],
        outputs=[chatbot, user_profile_state, msg],
        queue=True
    )

    # clear button to clear the chat history
    clear_button.click(
        lambda: (initial_greeting, None), None, [chatbot, user_profile_state], queue=False
    )
    chatbot.like(
    like,
    inputs=[chatbot, user_profile_state],
    outputs=[chatbot, user_profile_state]
    )

# Launch the Gradio app
port = int(os.environ.get("PORT", 8080))  # fallback 7860
demo.queue()  # Add this line before launch
demo.launch(
    show_error=True, 
    server_name="0.0.0.0", 
    server_port=port,
    share=False
)
