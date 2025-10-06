# PlanQK Assistant Chatbot - Milestone 4.1

An intelligent conversational AI assistant specifically designed for the PlanQK platform. This chatbot helps users navigate quantum computing, AI/ML solutions, and optimization services by providing context-aware, personalized responses powered by Azure OpenAI and Retrieval Augmented Generation (RAG).

## 🌟 Overview

The PlanQK Assistant is a sophisticated chatbot that automatically adapts its communication style based on user needs. It intelligently determines whether you're a business stakeholder or a technical developer, then tailors its responses accordingly - providing high-level insights for business users and detailed technical guidance for developers.

### Key Capabilities

- **🎯 Intelligent User Profiling**: Automatically detects if you're a business or technical user
- **📚 RAG-Powered Responses**: Retrieves relevant information from PlanQK knowledge base
- **💬 Streaming Conversations**: Real-time response generation for better user experience
- **📝 Chat History Management**: Save and resume conversations across sessions
- **🎨 Modern UI**: Clean, professional interface built with Gradio
- **📊 Full Observability**: OpenTelemetry instrumentation with Azure Application Insights

## 🏗️ Architecture

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    PlanQK Assistant                           │
│                                                               │
│  ┌─────────────────────┐      ┌────────────────────────┐    │
│  │ User Profile        │      │ Chat History           │    │
│  │ Detection (LLM)     │      │ Manager                │    │
│  │                     │      │                        │    │
│  │ • Business keywords │      │ • Load conversations   │    │
│  │ • Technical keywords│      │ • Save sessions        │    │
│  │ • GPT-4 classifier  │      │ • JSON persistence     │    │
│  └──────────┬──────────┘      └────────────────────────┘    │
│             │                                                 │
│             ▼                                                 │
│  ┌──────────────────────────────────────────────────┐        │
│  │          RAG Context Retrieval                   │        │
│  │                                                   │        │
│  │  1. Query transformation                         │        │
│  │  2. Azure Search (top 10 docs)                   │        │
│  │  3. Relevance filtering (strictness=1)           │        │
│  └──────────┬───────────────────────────────────────┘        │
│             │                                                 │
│             ▼                                                 │
│  ┌──────────────────────────────────────────────────┐        │
│  │     Response Generation (Azure OpenAI GPT-4)     │        │
│  │                                                   │        │
│  │  • System prompt (profile-specific)              │        │
│  │  • Retrieved context (RAG documents)             │        │
│  │  • Conversation history                          │        │
│  │  • Temperature: 0.1 (precise)                    │        │
│  │  • Stream: True (real-time)                      │        │
│  └──────────┬───────────────────────────────────────┘        │
│             │                                                 │
└─────────────┼─────────────────────────────────────────────────┘
              │
              ▼
       ┌──────────────┐
       │   Streaming  │
       │   Response   │
       │  + Citations │
       └──────────────┘

External Services:
┌─────────────────────┐  ┌──────────────────────┐  ┌─────────────────────┐
│  Azure OpenAI       │  │  Azure AI Search     │  │  App Insights       │
│  (GPT-4 Model)      │  │  (Knowledge Base)    │  │  (Telemetry)        │
└─────────────────────┘  └──────────────────────┘  └─────────────────────┘
```

### How It Works

1. **User Input Processing**: When you submit a question, the system analyzes your message
2. **Profile Detection**: An LLM classifies your query as either "business" or "technical" based on keywords and context
3. **Context Retrieval**: The system searches the PlanQK knowledge base (Azure Search) for relevant information
4. **Response Generation**: Azure OpenAI (GPT-4) generates a tailored response using:
   - Retrieved context from the knowledge base
   - Your detected user profile (business/technical)
   - Conversation history
5. **Streaming Output**: The response is streamed back to you in real-time

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Azure OpenAI API access with GPT-4 deployment
- Azure AI Search service with indexed PlanQK documentation
- (Optional) Azure Application Insights for monitoring

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
ENDPOINT_URL=https://your-resource.openai.azure.com/
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_KEY=your_azure_search_admin_key

# Optional
APPLICATIONINSIGHTS_CONNECTION_STRING=your_app_insights_connection_string
PORT=8080  # Default: 8080
```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd milestone4.0/milestone4.1
   ```

2. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env` (if provided)
   - Or export variables directly:
     ```bash
     export AZURE_OPENAI_API_KEY="your_key_here"
     export ENDPOINT_URL="your_endpoint_here"
     export SEARCH_ENDPOINT="your_search_endpoint_here"
     export SEARCH_KEY="your_search_key_here"
     ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the interface**
   - Open your browser and navigate to `http://localhost:8080`
   - Start chatting with the PlanQK Assistant!

## 🐳 Docker Deployment

### Using Docker (Recommended)

1. **Build the Docker image**
   ```bash
   # From the repository root
   cd /home/runner/work/milestone4.0/milestone4.0
   docker build -t planqk-assistant:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name planqk-chatbot \
     -p 8080:8080 \
     -e AZURE_OPENAI_API_KEY="your_key" \
     -e ENDPOINT_URL="your_endpoint" \
     -e SEARCH_ENDPOINT="your_search_endpoint" \
     -e SEARCH_KEY="your_search_key" \
     -e APPLICATIONINSIGHTS_CONNECTION_STRING="your_insights_string" \
     planqk-assistant:latest
   ```

3. **Access the application**
   - Navigate to `http://localhost:8080`

### Docker Compose (Alternative)

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  planqk-assistant:
    build: .
    ports:
      - "8080:8080"
    environment:
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - ENDPOINT_URL=${ENDPOINT_URL}
      - SEARCH_ENDPOINT=${SEARCH_ENDPOINT}
      - SEARCH_KEY=${SEARCH_KEY}
      - APPLICATIONINSIGHTS_CONNECTION_STRING=${APPLICATIONINSIGHTS_CONNECTION_STRING}
    restart: unless-stopped
```

Run with: `docker-compose up -d`

## 📁 Project Structure

```
milestone4.1/
├── app.py                  # Main application entry point & Gradio UI
├── business_mode.py        # Business user response handling logic
├── techy_mode.py          # Technical user response handling logic
├── user_profile.py        # User profile detection with LLM
├── chat_history.py        # Chat session persistence manager
├── utils.py               # Utility functions (keywords, profiling helpers)
├── styles.css             # Custom CSS styling for Gradio interface
└── README.md              # This file
```

### Component Details

#### `app.py` - Main Application
- **Gradio Interface**: Defines the chatbot UI with quick action buttons, chat history, and input controls
- **Streaming Logic**: Implements real-time response streaming using async generators
- **Event Handlers**: Manages user interactions (send, quick actions, like/dislike, chat loading)
- **OpenTelemetry Integration**: Instruments the app for monitoring and tracing

#### `user_profile.py` - User Profiling
- Uses a separate LLM call to classify user intent as "business" or "technical"
- Analyzes message content against predefined keywords from `utils.py`
- Caches profile per session to avoid repeated classification

#### `chat_history.py` - Session Management
- Saves conversations to JSON files in `chat_histories/` directory
- Supports loading previous chats, creating new chats, and deleting old ones
- Generates chat previews from first user message

#### `business_mode.py` & `techy_mode.py`
- Contains mode-specific response formatting logic
- Currently implements basic tagging; can be extended for mode-specific behavior

#### `utils.py` - Keyword Definitions
- Defines technical keywords: `code`, `algorithm`, `api`, `deployment`, etc.
- Defines business keywords: `cost`, `roi`, `license`, `compliance`, etc.
- Used by `user_profile.py` for profile detection

#### `styles.css` - UI Styling
- Custom PlanQK brand colors and modern design
- Gradient headers, styled buttons, and responsive layout

## 🎨 User Interface Features

### Quick Action Buttons
Three predefined prompts to help users get started:
- **🎯 Generate Use Case**: "Please tell me how to generate my first Use Case."
- **📊 PlanQK Use Cases Info**: "Please give me further information about PlanQK Use Cases"
- **🔧 Use Algorithm APIs**: "How can I use an Algorithm API?"

### Chat Management
- **Load Previous Chats**: Dropdown to select and resume past conversations
- **Start New Chat**: Create a fresh session (auto-saves current chat)
- **Chat History Persistence**: All conversations saved to `chat_histories/` directory

### Interactive Elements
- **Like/Dislike**: Provide feedback on responses
  - **Like**: Acknowledges helpful answer
  - **Dislike**: Automatically requests a more detailed response
- **Copy Button**: Copy any message to clipboard
- **Clear Button**: Reset conversation to initial state

## 🔧 Configuration

### System Prompt Customization

The system prompt is generated dynamically in `generate_system_prompt()` function in `app.py`. You can customize:
- Response tone and style
- Citation format
- Profile-specific instructions
- Output format requirements

### RAG Configuration

RAG settings are in the `post_request()` function in `app.py`:

```python
extra_body={
    "data_sources": [{
        "type": "azure_search",
        "parameters": {
            "endpoint": search_endpoint,
            "index_name": "rag-1749220504930",  # Change this
            "top_n_documents": 10,               # Number of docs to retrieve
            "strictness": 1,                     # Relevance threshold
            "in_scope": False,                   # Allow off-topic queries
            "query_type": "simple",              # Or "semantic"
            # ... more parameters
        }
    }]
}
```

### Telemetry Configuration

OpenTelemetry is configured in `app.py` and tracks:
- User profile classification
- RAG document retrieval
- LLM response generation
- Citations and sources used

Set `APPLICATIONINSIGHTS_CONNECTION_STRING` to enable Azure Application Insights.

## 📊 Monitoring & Observability

The application uses OpenTelemetry to provide detailed tracing:

### Traced Operations
1. **User Profiling**: How long it takes to classify user intent
2. **RAG Context Retrieval**: Document retrieval from Azure Search
3. **LLM Generation**: Response generation time and token usage

### Metrics Captured
- User profile (business/technical)
- Documents retrieved and used
- Model finish reason
- Response length
- Errors and exceptions

### Viewing Traces
- If `APPLICATIONINSIGHTS_CONNECTION_STRING` is set, view traces in Azure Portal
- Navigate to Application Insights → Performance → Dependencies
- Filter by operation name: "User-Profiling", "RAG-Context-Retrieval"

## 🧪 Testing

### Manual Testing
1. Start the application: `python app.py`
2. Open browser to `http://localhost:8080`
3. Test different user profiles:
   - **Business query**: "What is the cost of using PlanQK?"
   - **Technical query**: "How do I deploy an algorithm on PlanQK?"
4. Test chat features:
   - Send messages
   - Click quick action buttons
   - Like/dislike responses
   - Save and load chat history

### Profile Detection Testing
To verify user profiling works correctly:
- Check console output for: `"Identified User Profile: Technical"` or `"...Business"`
- Try messages with technical keywords vs. business keywords
- Observe response style differences

## 🐛 Troubleshooting

### Common Issues

**Issue: "Error initializing Azure OpenAI client"**
- **Cause**: Missing or invalid environment variables
- **Solution**: Verify `AZURE_OPENAI_API_KEY` and `ENDPOINT_URL` are set correctly
- **Check**: `echo $AZURE_OPENAI_API_KEY` (should not be empty)

**Issue: "No documents found in RAG retrieval"**
- **Cause**: Azure Search index is empty or index name is wrong
- **Solution**: Verify `SEARCH_ENDPOINT`, `SEARCH_KEY`, and index name (`rag-1749220504930`)
- **Check**: Test Azure Search API directly with Postman or curl

**Issue: "Connection timeout on application start"**
- **Cause**: Network issues or Azure service unavailable
- **Solution**: Check your internet connection and Azure service status
- **Workaround**: Increase timeout in Azure client initialization

**Issue: "Chat history not saving"**
- **Cause**: Permission issues on `chat_histories/` directory
- **Solution**: Ensure directory exists and is writable: `chmod 755 chat_histories/`

**Issue: "Telemetry not appearing in Azure"**
- **Cause**: Missing or invalid `APPLICATIONINSIGHTS_CONNECTION_STRING`
- **Solution**: Verify connection string format: `InstrumentationKey=...;IngestionEndpoint=...`
- **Note**: Telemetry is optional; app works without it

## 🔒 Security Considerations

- **Never commit secrets**: Use environment variables, not hardcoded keys
- **Use Azure Key Vault**: Store secrets securely in production
- **Rotate keys regularly**: Change API keys periodically
- **Limit search scope**: Set `in_scope: True` to restrict RAG to knowledge base only
- **Input validation**: User input is sanitized before sending to LLM
- **Rate limiting**: Consider adding rate limits for production deployment

## 📈 Performance Optimization

### Tips for Better Performance
1. **Use streaming**: Already implemented for real-time responses
2. **Cache user profiles**: Profile is cached per session (already implemented)
3. **Optimize RAG settings**:
   - Reduce `top_n_documents` if responses are too long
   - Increase `strictness` for more relevant results
4. **Use semantic search**: Change `query_type` to `"semantic"` for better retrieval
5. **Deploy close to Azure region**: Minimize latency by deploying near your Azure resources

### Scaling Considerations
- **Horizontal scaling**: Run multiple instances behind a load balancer
- **Persistent storage**: Move `chat_histories/` to shared storage (Azure Blob, DB)
- **Session management**: Implement Redis for session state across instances
- **Async processing**: Already uses async for streaming; good for concurrent users

## 🛠️ Development

### Adding New Features

**Adding a new quick action button**:
1. In `app.py`, find the Quick Actions section
2. Add a new button with unique ID:
   ```python
   question4_btn = gr.Button("🆕 New Action", elem_id="inline-q4")
   ```
3. Add click handler:
   ```python
   question4_btn.click(
       ask_predefined_question,
       inputs=[gr.State("Your question here"), chatbot, user_profile_state],
       outputs=[chatbot, user_profile_state, msg]
   )
   ```

**Customizing user profile detection**:
1. Edit `utils.py` to add/remove keywords
2. Modify `user_profile.py` `call_language_model()` for different classification logic
3. Adjust system prompt in `generate_system_prompt()` for different response styles

**Changing RAG behavior**:
1. In `app.py` `post_request()`, modify `extra_body["data_sources"]`
2. Adjust `top_n_documents`, `strictness`, `query_type`, etc.
3. Test with different index names if you have multiple knowledge bases

## 📚 Additional Resources

- **PlanQK Platform**: [https://platform.planqk.de/](https://platform.planqk.de/)
- **Azure OpenAI Docs**: [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- **Azure AI Search**: [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- **Gradio Documentation**: [Gradio Docs](https://www.gradio.app/docs/)
- **OpenTelemetry**: [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature: ..."`
5. Push to your fork: `git push origin feature/your-feature`
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💡 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Contact the PlanQK team
- Check existing issues for similar problems

---

**Built with ❤️ for the PlanQK Community**
