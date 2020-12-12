FROM python:3.9.0
WORKDIR /rmq-listener
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD app/* ./app/
CMD [ "python", "-u", "./app/main.py" ]