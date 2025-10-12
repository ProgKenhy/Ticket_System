import pika
from logging import getLogger

logger = getLogger(__name__)

def callback(ch, method, properties, body):
    logger.info(f"Received message: {body.decode()}")

def consume_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='fastapi_queue')

    channel.basic_consume(queue='fastapi_queue',
                          on_message_callback=callback,
                          auto_ack=True)

    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()