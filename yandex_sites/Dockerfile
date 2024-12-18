# final_alice/yandex_sites/Dockerfile
FROM python:3.11

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "site1.py"]
