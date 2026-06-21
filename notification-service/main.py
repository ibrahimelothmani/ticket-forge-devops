import asyncio
import json
import logging
import os
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
from fpdf2 import FPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotificationService")

app = FastAPI(title="TicketForge Notification & PDF Service")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CONFIRMED_TOPIC = "payment.confirmed"

def generate_ticket_pdf(order_id, user_id, seat_number, match_id):
    """
    دالة لتوليد ملف PDF حقيقي للتذكرة وحفظه محلياً داخل الحاوية
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    
    # تصميم بسيط للتذكرة
    pdf.cell(200, 10, txt="--- TICKETFORGE OFFICIAL TICKET ---", ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=f"Order ID: {order_id}", ln=1)
    pdf.cell(200, 10, txt=f"User ID: {user_id}", ln=1)
    pdf.cell(200, 10, txt=f"Match ID: {match_id}", ln=1)
    pdf.cell(200, 10, txt=f"Seat Number: {seat_number}", ln=1)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Thank you for using TicketForge! Enjoy the match.", ln=1, align="C")
    
    os.makedirs("/tmp/tickets", exist_ok=True)
    file_path = f"/tmp/tickets/ticket_{order_id}.pdf"
    pdf.output(file_path)
    return file_path

async def consume_payment_confirmations():
    """
    Worker للاستماع لأحداث الدفع الناجحة وتوليد التذاكر
    """
    consumer = AIOKafkaConsumer(
        CONFIRMED_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="notification-group",
        auto_offset_reset="earliest"
    )
    
    await consumer.start()
    logger.info(f"🚀 Notification Worker started. Listening on: {CONFIRMED_TOPIC}")
    
    try:
        async for msg in consumer:
            event_data = json.loads(msg.value.decode('utf-8'))
            order_id = event_data.get("orderId")
            user_id = event_data.get("userId")
            match_id = event_data.get("matchId", "M123") # افتراضي إذا لم يتوفر
            seat_number = event_data.get("seatNumber", "A-01") # افتراضي
            
            logger.info(f"✉️ Processing confirmation for Order ID: {order_id}")
            
            # 1. توليد الـ PDF
            pdf_path = generate_ticket_pdf(order_id, user_id, seat_number, match_id)
            logger.info(f"📄 Successfully generated PDF ticket at: {pdf_path}")
            
            # 2. محاكاة إرسال الإيميل
            logger.info(f"📧 Email sent successfully to user {user_id} with attached ticket_{order_id}.pdf")
            
    except Exception as e:
        logger.error(f"Error in Notification Consumer: {e}")
    finally:
        await consumer.stop()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_payment_confirmations())

@app.get("/health")
def health_check():
    return {"status": "UP", "service": "notification-service"}