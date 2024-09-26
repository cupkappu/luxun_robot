FROM python:3.10.14 AS base_build

WORKDIR /app
 
COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

FROM python:3.10.14

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/ /usr/local/lib/python3.10/
COPY --from=builder /app /app

CMD ["python", "/app/app.py"]