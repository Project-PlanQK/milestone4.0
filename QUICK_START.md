# 🚀 Quick Start Guide - PlanQK Assistant

**Get the PlanQK chatbot running in under 5 minutes!**

## ⚡ Fastest Way: Docker

### Step 1: Set Your Environment Variables

```bash
export AZURE_OPENAI_API_KEY="your_azure_openai_key"
export ENDPOINT_URL="https://your-resource.openai.azure.com/"
export SEARCH_ENDPOINT="https://your-search-service.search.windows.net"
export SEARCH_KEY="your_search_key"
```

### Step 2: Run with Docker

```bash
docker build -t planqk-assistant .
docker run -d -p 8080:8080 \
  -e AZURE_OPENAI_API_KEY \
  -e ENDPOINT_URL \
  -e SEARCH_ENDPOINT \
  -e SEARCH_KEY \
  planqk-assistant
```

### Step 3: Access the Chatbot

Open your browser: **http://localhost:8080** 🎉

---

## 🐍 Alternative: Python Direct

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your credentials
```

Or export directly:

```bash
export AZURE_OPENAI_API_KEY="your_key"
export ENDPOINT_URL="your_endpoint"
export SEARCH_ENDPOINT="your_search"
export SEARCH_KEY="your_search_key"
```

### Step 3: Run the Application

```bash
cd milestone4.1
python app.py
```

### Step 4: Access the Chatbot

Open your browser: **http://localhost:8080** 🎉

---

## 🔧 Using Docker Compose (Easiest)

### Step 1: Create .env file

```bash
cp .env.example .env
# Edit .env with your actual Azure credentials
```

### Step 2: Start Everything

```bash
docker-compose up -d
```

### Step 3: Check Status

```bash
docker-compose ps
docker-compose logs -f planqk-assistant
```

### Step 4: Access the Chatbot

Open your browser: **http://localhost:8080** 🎉

---

## 📋 Required Credentials

You'll need these from Azure Portal:

| Service | Where to Find |
|---------|---------------|
| **Azure OpenAI Key** | Azure Portal → OpenAI Service → Keys and Endpoint |
| **OpenAI Endpoint** | Azure Portal → OpenAI Service → Keys and Endpoint |
| **Search Endpoint** | Azure Portal → AI Search → Overview → URL |
| **Search Key** | Azure Portal → AI Search → Keys → Admin Keys |

---

## 🎯 Try These Questions

Once the chatbot is running, try:

**Business Questions:**
- "What is the cost of using PlanQK?"
- "How can PlanQK help my business?"
- "What are the main use cases?"

**Technical Questions:**
- "How do I deploy an algorithm on PlanQK?"
- "Show me how to use the API"
- "What programming languages are supported?"

---

## 🐛 Troubleshooting

### "Error initializing Azure OpenAI client"
→ Check your `AZURE_OPENAI_API_KEY` and `ENDPOINT_URL`

### "Cannot connect to Azure Search"
→ Verify `SEARCH_ENDPOINT` and `SEARCH_KEY`

### "Port 8080 already in use"
→ Change the port: `docker run -p 8081:8080 ...` or `export PORT=8081`

### "Module not found"
→ Run: `pip install -r requirements.txt`

---

## 📚 Need More Help?

- **Full Documentation**: [milestone4.1/README.md](milestone4.1/README.md)
- **Root README**: [README.md](README.md)
- **GitHub Issues**: Open an issue for support

---

**That's it! You're ready to go! 🚀**
