import pika

def publish_message(message: str):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            credentials=pika.PlainCredentials('user', 'password')
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue='fastapi_queue', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='fastapi_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    connection.close()