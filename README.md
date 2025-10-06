# PlanQK Assistant Chatbot

An intelligent conversational AI assistant for the PlanQK platform, powered by Azure OpenAI and featuring automatic user profiling for personalized responses.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Azure](https://img.shields.io/badge/Azure-OpenAI-blue.svg)

## 🚀 Quick Start

The PlanQK Assistant is a sophisticated chatbot that adapts its communication style based on whether you're a business stakeholder or technical developer, providing tailored responses using Retrieval Augmented Generation (RAG) from the PlanQK knowledge base.

### Key Features

- 🎯 **Intelligent User Profiling** - Automatically detects business vs. technical users
- 📚 **RAG-Powered Responses** - Retrieves relevant information from PlanQK documentation
- 💬 **Real-time Streaming** - Live response generation for better UX
- 📝 **Chat History** - Save and resume conversations across sessions
- 🎨 **Modern UI** - Clean, professional Gradio interface
- 📊 **Full Observability** - OpenTelemetry integration with Azure Application Insights

## 📖 Documentation

**For complete documentation, setup instructions, and usage guides, see:**
### **[milestone4.1/README.md](./milestone4.1/README.md)** 📚

The main application code is in the `milestone4.1/` directory.

## 🏃 Quick Run

### Using Docker (Recommended)

```bash
# Build the image
docker build -t planqk-assistant:latest .

# Run the container
docker run -d -p 8080:8080 \
  -e AZURE_OPENAI_API_KEY="your_key" \
  -e ENDPOINT_URL="your_endpoint" \
  -e SEARCH_ENDPOINT="your_search_endpoint" \
  -e SEARCH_KEY="your_search_key" \
  planqk-assistant:latest
```

Access at: `http://localhost:8080`

### Using Python Directly

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_OPENAI_API_KEY="your_key"
export ENDPOINT_URL="your_endpoint"
export SEARCH_ENDPOINT="your_search_endpoint"
export SEARCH_KEY="your_search_key"

# Run the application
cd milestone4.1
python app.py
```

## 🏗️ Project Structure

```
milestone4.0/
├── milestone4.1/          # 📂 Main application (see its README for details)
│   ├── app.py            # Main application & Gradio UI
│   ├── user_profile.py   # User profiling with LLM
│   ├── chat_history.py   # Session management
│   ├── business_mode.py  # Business user logic
│   ├── techy_mode.py     # Technical user logic
│   ├── utils.py          # Utility functions & keywords
│   ├── styles.css        # Custom UI styling
│   └── README.md         # 📖 Detailed documentation
├── Dockerfile            # Docker container configuration
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── Versioning/          # System prompt version history
```

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_API_KEY` | ✅ Yes | Azure OpenAI API key |
| `ENDPOINT_URL` | ✅ Yes | Azure OpenAI endpoint URL |
| `SEARCH_ENDPOINT` | ✅ Yes | Azure AI Search service endpoint |
| `SEARCH_KEY` | ✅ Yes | Azure AI Search admin key |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | ❌ No | Azure Application Insights (optional) |
| `PORT` | ❌ No | Port to run on (default: 8080) |

## 🎯 What This Chatbot Does

The PlanQK Assistant helps users by:

1. **Understanding User Intent**: Classifies queries as business or technical
2. **Retrieving Context**: Searches PlanQK documentation for relevant information
3. **Generating Responses**: Uses Azure OpenAI (GPT-4) to create tailored answers
4. **Providing Citations**: Includes sources from PlanQK documentation
5. **Managing Conversations**: Saves chat history for continuity

### Example Interactions

**Business User:**
> "What is the cost of using PlanQK services?"

→ Gets high-level explanation with ROI considerations and pricing information

**Technical User:**
> "How do I deploy a quantum algorithm using the API?"

→ Gets step-by-step technical instructions with code examples and API endpoints

## 🧪 Architecture Overview

```
User Query → Profile Detection → RAG Retrieval → GPT-4 Generation → Streaming Response
                  ↓                    ↓
            LLM Classifier      Azure Search
            (GPT-4)            (PlanQK Docs)
```

## 🐳 Docker Information

The included `Dockerfile`:
- Uses Python 3.11 base image
- Installs all dependencies from `requirements.txt`
- Copies application files from `milestone4.1/` directory
- Exposes port 8080
- Configures Gradio for external access
- Runs `app.py` on container start

## 🛠️ Development

### Prerequisites
- Python 3.11+
- Azure OpenAI API access with GPT-4 model
- Azure AI Search service with PlanQK documentation indexed
- Docker (optional, for containerized deployment)

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd milestone4.0/milestone4.1

# Install in development mode
pip install -r ../requirements.txt

# Run with auto-reload (if using uvicorn mode)
python app.py
```

### Testing
- Manual testing via web interface at `http://localhost:8080`
- Test different user profiles with business vs. technical queries
- Verify RAG retrieval by checking cited sources
- Monitor telemetry in Azure Application Insights (if configured)

## 📊 Monitoring

When `APPLICATIONINSIGHTS_CONNECTION_STRING` is configured, the application provides:
- Request traces with user profiling info
- RAG document retrieval metrics
- LLM response generation timing
- Error tracking and debugging

View in Azure Portal → Application Insights → Performance

## 🔒 Security Notes

- Never commit API keys or secrets to version control
- Use environment variables or Azure Key Vault for secrets
- Regularly rotate API keys
- Review Azure Search access control settings
- Consider rate limiting for production deployments

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a Pull Request

See [milestone4.1/README.md](./milestone4.1/README.md) for detailed development guidelines.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: See [milestone4.1/README.md](./milestone4.1/README.md)
- **PlanQK Platform**: [https://platform.planqk.de/](https://platform.planqk.de/)

---

**Built with ❤️ for the PlanQK Community** | Powered by Azure OpenAI & Gradio
