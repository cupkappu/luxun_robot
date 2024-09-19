FROM python:3.10.14

WORKDIR /app
 
ADD . .

RUN pip install -r requirements.txt

CMD ["python", "/app/app.py"]