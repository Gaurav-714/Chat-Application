FROM python:3.12-slim

WORKDIR /chat-app

COPY . .

RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]