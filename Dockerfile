FROM python:3.11

ENV PORT=7080
ENV GRADIO_SERVER_PORT=${PORT}
ENV GRADIO_SERVER_NAME=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install openai

COPY apptest.py business_mode.py techy_mode.py styles.css ./

EXPOSE 7080

CMD ["python", "apptest.py"]
