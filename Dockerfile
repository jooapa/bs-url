FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
COPY start.sh .
COPY .env .env
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client
COPY app/ .
RUN chmod +x start.sh
CMD ["./start.sh"]