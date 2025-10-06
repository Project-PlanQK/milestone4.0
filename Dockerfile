FROM python:3.11

# Set working directory
WORKDIR /app

# Environment variables for Gradio server configuration
ENV PORT=8080
ENV GRADIO_SERVER_PORT=${PORT}
ENV GRADIO_SERVER_NAME=0.0.0.0

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files from milestone4.1 directory
COPY milestone4.1/app.py .
COPY milestone4.1/business_mode.py .
COPY milestone4.1/techy_mode.py .
COPY milestone4.1/user_profile.py .
COPY milestone4.1/utils.py .
COPY milestone4.1/chat_history.py .
COPY milestone4.1/styles.css .

# Create directory for chat histories
RUN mkdir -p chat_histories

# Expose port for Gradio application
EXPOSE 8080

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD ["python", "app.py"]
