#!/usr/bin/env python3
import os
import time
import pika

QUEUE_URL = os.getenv('QUEUE_URL', 'amqp://guest:guest@localhost:5672')

def process_message(ch, method, properties, body):
    print(f" [x] Received {body}")
    time.sleep(1)  # Simulate processing
    print(f" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    print(f"Connecting to RabbitMQ at {QUEUE_URL}")
    parameters = pika.URLParameters(QUEUE_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    channel.queue_declare(queue='task_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=process_message)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
