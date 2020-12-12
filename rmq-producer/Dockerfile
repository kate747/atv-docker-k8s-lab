FROM python:3.9.0-alpine3.12
WORKDIR /rmq-producer
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD app/* ./app/
CMD [ "python", "-u", "./app/main.py" ]