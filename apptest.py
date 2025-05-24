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


print("Skript startet") #debug

# Define a function to post a request to the Azure OpenAI model
def post_request(messages):
    # Get environment variables for the configuration
    endpoint = os.getenv("ENDPOINT_URL") #url of the Azure OpenAI endpoint
    #deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.getenv("SEARCH_ENDPOINT") #url of the Azure Search endpoint
    search_key = os.getenv("SEARCH_KEY") #using azure search key for the vector database (bot can search in the database)
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY") # Azure OpenAI API Key
    
    try:
        # Initialize Azure OpenAI Service client with key-based authentication
        # here a connection to the Azure OpenAI service is established
        client = AzureOpenAI(
            api_key=subscription_key,
            azure_endpoint=endpoint,  # Nur Domain, ohne /openai/
            #api_version=api_version,
            api_version="2025-01-01-preview",
        )
        
        # Prepare the chat prompt by appending the user message to the conversation
        # change prompt based on the selected mode
        """if messages[0]["content"] == "Business Mode Activated.":
            messages = handle_business(messages)
        elif messages[0]["content"] == "Tech Mode Activated.":
            messages = handle_techy(messages)"""
        

        # Initialize the chat prompt with a system message
        # The system message sets the context for the conversation
        chat_prompt = [
            {
                "role": "system",
                "content": """
You are a helpful virtual assistant for the PlanQK platform (https://platform.planqk.de/home). Your job is to help users complete their tasks using only the retrieved context from PlanQK resources.

Guidelines:
- Respond strictly based on the retrieved context. Do not use prior knowledge or assumptions.
- If information is missing, ask focused follow-up questions.
- Avoid restricted topics: politics, religion, legal/medical/financial advice, personal matters, or criticism.
- Maintain a professional, concise, and friendly tone for a technical/business audience.
- Vary your phrasing, even when using sample phrases.
- Always end with: "Is there anything else I can help you with on PlanQK?"

Response Format:
- Include a final message in every response.
- Cite retrieved sources as: source: https://platform.planqk.de/[path]
- Only respond to questions relevant to the PlanQK platform.

Sample Phrases for Deflecting:
- "I'm sorry, but I'm unable to discuss that topic. Is there something else I can help you with?"
- "That's not something I can provide information on, but I'm happy to help with questions related to PlanQK."

Example Dialogue:
User: We’re exploring AI for operational optimization. Can PlanQK support us?
Assistant: Thanks for reaching out! PlanQK offers AI models and services for analytics and optimization. Could you share:
- What kind of data you’re working with?
- Are you evaluating or ready to deploy?

User: We have structured time-series data and want to explore.
Assistant: Great. Check out:
- Use Case: “Predictive Optimization for Dynamic Systems” [UseCase_X](ucX)
- Model: “Generic AI Optimizer” [AI_Opt_Model](mX)

Would you like help setting up a workspace or connecting data?

User: Yes, please.
Assistant: Here's how to start:
1. Create a workspace under “Workspaces”.
2. Add the model via the “Services” tab.
3. Connect data via “Data Connectors”.
4. Run a test with sample data.

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
                "index_name": "vector-1747684712810c",
                "semantic_configuration": "",
                "authentication": {
                    "type": "api_key",
                    "key": search_key
                },
                "query_type": "simple",
                "in_scope": False, #setting in_scope to false means, that documents not belonging to the database or topic will be used and searched additionally
                #"role_information": "You are an AI assistant that helps people find information.",
                "strictness": 1, # strictness of the search results (0-5). 0 means no strictness, 5 means very strict. The stricter the search, the more relevant the results are. The strictness has to be between 1 and 5, where 1 allows a greater variety in answers with more data being seen as possibly relevant
                "top_n_documents": 5 # number of documents to retrieve from the search (1-10). The more documents are retrieved, the more relevant the results are. The top_n_documents has to be between 1 and 10, where 1 means only one document is retrieved and 10 means all documents are retrieved.
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
async def bot_simple(history):
    try:
        bot_response = post_request(history)
        history.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
    return history, gr.update(interactive=True, value="") ## Clear the message box after sending

#for thinking LLM
async def bot_with_thinking(user_message, history):
    if not user_message.strip():
        # if no message is entered
        history.append({"role": "assistant", "content": "Please type a message first!"})
        yield history, gr.update(value="", interactive=True)
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
        yield history, gr.update(interactive=False)  # Update the chatbot with the thinking phrase 

    # remove thinking messages from history to show only the final answer
    history = [msg for msg in history if not any(p in msg["content"] for p in thinking_phrases)]

    #Bot-Output, get real response from OpenAI
    try:
        bot_response = post_request(history)
        history.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error during OpenAI request: {e}"})
        
    yield history, gr.update(value="",interactive=True)  # Update the chatbot with the final response ## Clear the message box after sending
    
    #if user sends  a message, append it to the history and show it in the chat
def user(user_message, history):
    history.append({"role": "user", "content": user_message})
    return "", history
    #return "", history + [{"role": "user", "content": user_message}]

def like(evt: gr.LikeData):
    print("User liked the response")
    print(evt.index, evt.liked, evt.value)


initial_greeting = [{"role": "assistant", "content": "Hey! I am a Chatbot and I'm here to assist you! Please select a mode first. You can choose between Business and Techy mode."}]

#add custom CSS styles to the Gradio app
with open("styles.css") as styles:
    styles_css = styles.read()

# Create a Gradio chat interface
with gr.Blocks(css=styles_css) as demo:
    gr.Markdown("<h2 style='text-align: center;'>Helping Chatbot</h2>")
    chatbot = gr.Chatbot(value=initial_greeting, type="messages")
    state = gr.State(value=initial_greeting)

    with gr.Row():
        business_button = gr.Button("Business", elem_classes="blue-button")
        techy_button = gr.Button("Techy", elem_classes="blue-button")
    
    selected_mode = gr.State(value="")  # which mode is active (business/techy)

    # Handle mode button clicks to set the mode
    business_button.click(fn=lambda history: history + [{"role": "assistant", "content": "Business Mode Activated."}],
                          inputs=chatbot, outputs=chatbot)
    
    techy_button.click(fn=lambda history: history + [{"role": "assistant", "content": "Tech Mode Activated."}],
                       inputs=chatbot, outputs=chatbot)

    with gr.Row():
        with gr.Column(scale=6):
            msg = gr.Textbox(label="Message", scale=3)  # left side, larger space
        with gr.Column(scale=2):  # right side, smaller space
            thinking_button = gr.Button("Thinking LLM", elem_classes="pink-button") #make button pink
            clear_button = gr.Button("Clear", elem_classes="pink-button") #make button pink

    #handle the thinking button click
    thinking_button.click(bot_with_thinking, inputs=[msg, chatbot], outputs=[chatbot, msg])#.then(bot_with_thinking, inputs=chatbot, outputs=[chatbot, msg])
    #thinking_button.click(bot_with_thinking, inputs=chatbot, outputs=[chatbot, msg])
   
    #handle textbox submit
        #invoke the user function and update the textbox and chat history
        #then call the bot_with_thinking function to get the response from the bot
    msg.submit(user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
        bot_simple, inputs=chatbot, outputs=[chatbot, msg]
    )

    # clear button to clear the chat history
    clear_button.click(lambda: None, None, chatbot, queue=False)
    chatbot.like(like)

# Launch the Gradio app
port = int(os.environ.get("PORT", 8080))  # fallback
demo.launch(show_error=True, server_name="0.0.0.0", server_port=port)
