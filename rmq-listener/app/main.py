import pika
import os
import psycopg2
import json

RMQ_ENDPOINT = os.environ["RMQ_ENDPOINT"]
RMQ_QUEUE = os.environ["RMQ_QUEUE"]
RMQ_USERNAME = os.environ["RMQ_USERNAME"]
RMQ_PASSWORD = os.environ["RMQ_PASSWORD"]
RMQ_PORT = os.getenv("RMQ_PORT", 5672)
RMQ_VH = os.getenv("RMQ_VH", "/")

POSTGRES_ENDPOINT = os.environ["POSTGRES_ENDPOINT"]
POSTGRES_USERNAME = os.environ["POSTGRES_USERNAME"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DATABASE = os.environ["POSTGRES_DATABASE"]
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

postgres_conn = psycopg2.connect(database=POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD,
                                 host=POSTGRES_ENDPOINT, port=POSTGRES_PORT)
postgres_cursor = postgres_conn.cursor()


def callback(ch, method, properties, body):
    print(f"Got event -- ch: {ch}, method: {method}, props: {properties}, body: {body}")
    event = json.loads(body)
    event_type = event.get('eventType', 'UNDEFINED')
    data = event['data']
    if event_type == 'USER':
        postgres_cursor.execute("INSERT INTO users (id, name, email) VALUES (%s, %s, %s)",
                                (data['id'], data['name'], data['email']))
    elif event_type == 'ORDER':
        postgres_cursor.execute(
            "INSERT INTO orders (id, user_id, total_count, order_timestamp) VALUES (%s, %s, %s, %s)",
            (data['id'], data['userId'], data['totalCount'], data['orderTimestamp']))
    else:
        print(f"EventType: {event_type} is not supported. Only USER and ORDER are")
        return

    postgres_conn.commit()
    print(f'Event -- {data} -- has been successfully persisted')


rmq_conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=RMQ_ENDPOINT,
    port=RMQ_PORT,
    virtual_host=RMQ_VH,
    credentials=pika.PlainCredentials(username=RMQ_USERNAME, password=RMQ_PASSWORD)
))

channel = rmq_conn.channel()

channel.basic_consume(queue=RMQ_QUEUE, auto_ack=True, on_message_callback=callback)

print(f"Starting to consume from {RMQ_QUEUE} queue")

channel.start_consuming()

rmq_conn.close()
postgres_cursor.close()
postgres_conn.close()
