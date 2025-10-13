# простенький пример consumer написанный ИИ (для ознакомления с работой rabbitMQ)

import pika
import logging
import time
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def callback(ch, method, properties, body):
    logger.info("🎯 CALLBACK TRIGGERED!")
    logger.info(f"📨 Received message: {body.decode()}")
    logger.info(f"📊 Delivery tag: {method.delivery_tag}")
    logger.info(f"🔧 Properties: {properties}")


def consume_message():
    logger.info("🚀 Starting consumer...")

    while True:
        try:
            logger.info("🔗 Attempting to connect to RabbitMQ...")

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    credentials=pika.PlainCredentials('user', 'password'),
                    heartbeat=600
                )
            )
            channel = connection.channel()

            result = channel.queue_declare(queue='fastapi_queue', durable=True)
            logger.info(f"📋 Queue declared. Message count: {result.method.message_count}")

            def detailed_callback(ch, method, properties, body):
                logger.info("=" * 50)
                logger.info("🎯 NEW MESSAGE RECEIVED!")
                logger.info(f"📨 Body: {body.decode()}")
                logger.info(f"📊 Delivery tag: {method.delivery_tag}")
                logger.info(f"🔧 Headers: {properties.headers}")
                logger.info(f"📫 Exchange: {method.exchange}")
                logger.info(f"🔑 Routing key: {method.routing_key}")
                logger.info("=" * 50)

                time.sleep(2)
                logger.info("✅ Message processing completed")

            channel.basic_consume(
                queue='fastapi_queue',
                on_message_callback=detailed_callback,
                auto_ack=True
            )

            logger.info('✅ Connected to RabbitMQ. Waiting for messages...')
            logger.info('⏳ Consumer is actively listening...')

            channel.start_consuming()

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            logger.info("🔄 Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    logger.info("🚀 CONSUMER SCRIPT STARTED")
    consume_message()