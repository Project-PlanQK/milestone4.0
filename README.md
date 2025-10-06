# PlanQK Assistant Chatbot
#### !IMPORTANT! This is the chatbot you can find at [hhz-dbe-jahresprojekt](https://platform.planqk.de/use-cases/67d0b819-65e5-4856-98c4-30a997bf60d3/demo). (You need an account with Planqk and authorization for the use case. For further information, please contact the creators of the repository.)
#### If you are looking for the readme for the latest version, please open the milestone4.1 subfolder.

A conversational AI assistant built with Gradio that helps users navigate the PlanQK platform, powered by Azure OpenAI services and featuring automatic user profiling for personalized responses.

## Features

- **Adaptive Response System**
  - Automatic user profiling (Business/Technical)
  - Context-aware responses using RAG (Retrieval Augmented Generation)
  - Streaming responses for better user experience

- **Interactive UI**
  - Clean, modern interface built with Gradio
  - Quick-access question buttons
  - Like/dislike feedback system
  - Chat history management
  - Message copying functionality

- **Enterprise Integration**
  - Azure OpenAI integration
  - Azure Search for knowledge base queries
  - OpenTelemetry instrumentation for monitoring
  - Docker containerization support

## Prerequisites

- Python 3.11+
- Azure OpenAI API access
- Azure Search service
- Azure Application Insights (optional)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd planqk-assistant

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
AZURE_OPENAI_API_KEY=your_api_key
ENDPOINT_URL=your_azure_endpoint
SEARCH_ENDPOINT=your_search_endpoint
SEARCH_KEY=your_search_key
APPLICATIONINSIGHTS_CONNECTION_STRING=your_insights_connection_string

## Usage

Running locally
Start the chatbot server:
```bash
python app.py
```

Access the web interface at http://localhost:8080

Using Docker
1. Build the container:
```bash
docker build -t planqk-assistant .
```
2. Run the container:
```bash
docker run -p 7860:7860 \
  -e AZURE_OPENAI_API_KEY=your_key \
  -e ENDPOINT_URL=your_endpoint \
  -e SEARCH_ENDPOINT=your_search_endpoint \
  -e SEARCH_KEY=your_search_key \
  planqk-assistant
  ```

## Project Structure
├── app.py                  # Main application entry point
├── business_mode.py        # Business user response handling
├── chat_history.py        # Chat history management
├── styles.css             # UI styling
├── techy_mode.py          # Technical user response handling
├── user_profile.py        # User profiling logic
├── utils.py              # Utility functions
└── Dockerfile            # Container configuration

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---
**Built for the PlanQK Assistant Project**
