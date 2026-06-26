import asyncio
import json
import logging
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from prometheus_fastapi_instrumentator import Instrumentator

    
# إعداد الـ Logging لمراقبة العمليات من طرف الـ DevOps
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PaymentService")

app = FastAPI(title="TicketForge Payment Service")

# الإعدادات الخاصة بالـ Kafka Broker
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CONSUME_TOPIC = "ticket.reserved"
PRODUCER_CONFIRMED_TOPIC = "payment.confirmed"
PRODUCER_FAILED_TOPIC = "payment.failed"


@app.on_event("startup")
async def startup_event():
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("🚀 Prometheus metrics endpoint is now available at /metrics")

    
async def consume_ticket_reservations():
    """
    Background worker للاستماع للأحداث القادمة من ticket-service
    """
    consumer = AIOKafkaConsumer(
        CONSUME_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="payment-group",
        auto_offset_reset="earliest"
    )
    
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    
    await consumer.start()
    await producer.start()
    
    logger.info(f"🚀 Started consuming from topic: {CONSUME_TOPIC}")
    
    try:
        async for msg in consumer:
            event_data = json.loads(msg.value.decode('utf-8'))
            order_id = event_data.get("orderId")
            user_id = event_data.get("userId")
            
            logger.info(f"💳 Received reservation event for Order ID: {order_id} by User: {user_id}")
            
            # محاكاة البزنس لوجيك للدفع (Mock Payment Logic)
            # سنعتبر العملية ناجحة دائماً إلا إذا كان رقم الطلب مضاعف لـ 7 لمحاكاة الأخطاء والفشل
            payment_success = True if order_id % 7 != 0 else False
            
            payload = {
                "orderId": order_id,
                "userId": user_id,
                "amount": 50.00, # سعر تذكرة وهمي
                "status": "SUCCESS" if payment_success else "FAILED"
            }
            
            if payment_success:
                logger.info(f"✅ Payment SUCCESS for Order ID: {order_id}. Polling confirmed event...")
                await producer.send_and_wait(PRODUCER_CONFIRMED_TOPIC, json.dumps(payload).encode('utf-8'))
            else:
                logger.error(f"❌ Payment FAILED for Order ID: {order_id}. Polling failed event...")
                await producer.send_and_wait(PRODUCER_FAILED_TOPIC, json.dumps(payload).encode('utf-8'))
                
    except Exception as e:
        logger.error(f"Error in Kafka Consumer/Producer: {e}")
    finally:
        await consumer.stop()
        await producer.stop()

@app.on_event("startup")
async def startup_event():
    # إطلاق الـ Kafka Consumer في الخلفية عند تشغيل السيرفيس مباشرة
    asyncio.create_task(consume_ticket_reservations())

@app.get("/health")
def health_check():
    return {"status": "UP", "service": "payment-service"}