import os
import time
import uuid
import random
import json

import pika

RMQ_ENDPOINT = os.environ["RMQ_ENDPOINT"]
RMQ_QUEUE = os.environ["RMQ_QUEUE"]
RMQ_USERNAME = os.environ["RMQ_USERNAME"]
RMQ_PASSWORD = os.environ["RMQ_PASSWORD"]
RMQ_PORT = os.getenv("RMQ_PORT", 5672)
RMQ_VH = os.getenv("RMQ_VH", "/")


def generate_user():
    user_id = str(uuid.uuid4())
    return {
        'id': user_id,
        'name': f'{user_id} name',
        'email': f'{user_id}@f{random.choice(emails)}'
    }


def generate_order(user_id):
    return {
        'id': str(uuid.uuid4()),
        'userId': user_id,
        'totalCount': round(random.uniform(10, 1000), 2),
        'orderTimestamp': round(time.time())
    }


emails = ['gmail.com', 'amazon.com', 'mail.com']

users = [generate_user() for _ in range(10)]

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=RMQ_ENDPOINT,
    port=RMQ_PORT,
    virtual_host=RMQ_VH,
    credentials=pika.PlainCredentials(username=RMQ_USERNAME, password=RMQ_PASSWORD)
))

channel = conn.channel()

print(f"Publishing messages into {RMQ_QUEUE} queue")

try:
    for user in users:
        channel.basic_publish(exchange='',
                              routing_key=RMQ_QUEUE,
                              body=json.dumps({
                                  'eventType': 'USER',
                                  'data': user
                              }),
                              properties=pika.BasicProperties(content_type='application/json'))

    print(f"User data of {user} has been sent to RMQ")

    while True:
        orders = [generate_order(random.choice(users)['id']) for _ in range(100)]

        for order in orders:
            channel.basic_publish(exchange='',
                                  routing_key=RMQ_QUEUE,
                                  body=json.dumps({
                                      'eventType': 'ORDER',
                                      'data': order
                                  }),
                                  properties=pika.BasicProperties(content_type='application/json'))

            print(f"Order data {order} has been sent to RMQ")

        print("Sleeping for the next 30 seconds awaiting for the batch")
        time.sleep(30)
finally:
    conn.close()
