FROM python:3.9-slim

WORKDIR /app

COPY . .


RUN python -m pip install --upgrade pip && pip install -r requirements.txt 


EXPOSE 8000

CMD ["python", "app.py"]