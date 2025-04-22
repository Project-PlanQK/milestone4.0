FROM python:3.11

ENV PORT=7860
ENV GRADIO_SERVER_PORT=${PORT}
ENV GRADIO_SERVER_NAME=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install openai

COPY apptest.py apptest.py

EXPOSE 7860

CMD ["python", "apptest.py"]
