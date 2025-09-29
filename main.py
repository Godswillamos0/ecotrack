import smtplib
import schedule
import time
import threading
from email.message import EmailMessage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from chat import chat
from dotenv import load_dotenv
import os


from sqlalchemy.orm import Session
from fastapi import FastAPI
import models
from database import engine
from routers import auth, chat



models.Base.metadata.create_all(bind=engine)

# Load API key from .env
load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

# Email Config (you should move these to environment variables in production)
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Your email address
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Your email password or app-specific password
RECIPIENT = os.getenv('RECIPIENT')  # Recipient email address

# Define the two different times and messages
SCHEDULES = [
    {
        "time": "08:00",  # Morning email
        "subject": "Good Morning! Ecotraca",
        "message": f"This is your morning message. {chat("email_ID", "Give me tips for a green living")}"
    },
    {
        "time": "23:37",  # Evening email
        "subject": "Good Evening! Ecotraca",
        "message": """Reminder: Hope you had a productive day!
        You can also ask me about your carbon footprint and how to reduce it. Just reply to this email with your activities! 
        """
    }
]

def send_email(subject: str, content: str):
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email '{subject}' sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send '{subject}' email:", e)

def run_scheduler():
    print("⏳ Scheduler started. Setting up daily emails...")

    for schedule_item in SCHEDULES:
        schedule.every().day.at(schedule_item['time']).do(
            send_email,
            subject=schedule_item['subject'],
            content=schedule_item['message']
        )
        print(f"📅 Scheduled '{schedule_item['subject']}' at {schedule_item['time']}.")

    while True:
        schedule.run_pending()
        time.sleep(1)

@app.on_event("startup")
def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

@app.get("/")
def home():
    return {
        "message": "FastAPI app is running with scheduled morning and evening emails.",
        "schedules": SCHEDULES
    } 


  
