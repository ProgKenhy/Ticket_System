import pika
import time
from core.logger import logger


def callback(ch, method, properties, body):
    message = body.decode()
    logger.info(f"Обработано: {message}")


def consume_message():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    credentials=pika.PlainCredentials('user', 'password')
                )
            )
            channel = connection.channel()

            channel.queue_declare(queue='fastapi_queue', durable=True)
            channel.basic_consume(queue='fastapi_queue', on_message_callback=callback, auto_ack=True)

            logger.info("Воркер запущен. Ожидание сообщений...")
            channel.start_consuming()

        except Exception as e:
            logger.error(f"Ошибка {e}\nПереподключение через 5 секунд...")
            time.sleep(5)


if __name__ == "__main__":
    consume_message()