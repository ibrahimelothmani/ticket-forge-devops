import asyncio
import json
import logging
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PaymentService")

app = FastAPI(title="TicketForge Payment Service")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CONSUME_TOPIC = "ticket.reserved"
PRODUCER_CONFIRMED_TOPIC = "payment.confirmed"
PRODUCER_FAILED_TOPIC = "payment.failed"


async def consume_ticket_reservations():
    while True:
        try:
            consumer = AIOKafkaConsumer(
                CONSUME_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="payment-group",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )

            producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

            await consumer.start()
            await producer.start()

            logger.info(f"Started consuming from topic: {CONSUME_TOPIC}")

            async for msg in consumer:
                event_data = json.loads(msg.value.decode('utf-8'))
                order_id = event_data.get("orderId")
                user_id = event_data.get("userId")

                logger.info(f"Received reservation event for Order ID: {order_id} by User: {user_id}")

                payment_success = order_id % 7 != 0

                payload = {
                    "orderId": order_id,
                    "userId": user_id,
                    "amount": 50.00,
                    "status": "SUCCESS" if payment_success else "FAILED"
                }

                if payment_success:
                    logger.info(f"Payment SUCCESS for Order ID: {order_id}. Sending confirmed event...")
                    await producer.send_and_wait(PRODUCER_CONFIRMED_TOPIC, json.dumps(payload).encode('utf-8'))
                else:
                    logger.error(f"Payment FAILED for Order ID: {order_id}. Sending failed event...")
                    await producer.send_and_wait(PRODUCER_FAILED_TOPIC, json.dumps(payload).encode('utf-8'))

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Kafka error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


@app.on_event("startup")
async def startup():
    asyncio.create_task(consume_ticket_reservations())


@app.get("/health")
def health_check():
    return {"status": "UP", "service": "payment-service"}
