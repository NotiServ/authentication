import os
import psycopg2
from psycopg2 import sql
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from rq import Queue, Connection, Worker
from rq.job import Job
# config.py
# from my_worker import conn as redisconn
import redis
# Load environment variables from .env file
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

# Redis connection
REDIS_URL = os.getenv('REDIS_URL')
redisconn = redis.from_url(REDIS_URL)

if __name__ == '__main__':
    with Connection(redisconn):
        worker = Worker(map(Queue, ['default']))
        worker.work()

# Redis connection and queue
q = Queue(connection=redisconn)

# Create tables if not exists
# cur.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id SERIAL PRIMARY KEY,
#         username VARCHAR(255) NOT NULL,
#         email VARCHAR(255) NOT NULL,
#         phone VARCHAR(10) NOT NULL,
#         password VARCHAR(255) NOT NULL,
#         account_status VARCHAR(255) DEFAULT 'active',
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS verification (
#         id SERIAL PRIMARY KEY,
#         user_id INT REFERENCES users(id) NOT NULL,
#         sms_otp VARCHAR(255) NOT NULL,
#         email_otp VARCHAR(255) NOT NULL,
#         sms_otp_status VARCHAR(255) DEFAULT 'pending',
#         email_otp_status VARCHAR(255) DEFAULT 'pending',
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP            
#     )   
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS recipient_data (
#         id SERIAL PRIMARY KEY,
#         user_id INT REFERENCES users(id) NOT NULL,
#         recipient_name VARCHAR(255) NOT NULL,
#         recipient_email VARCHAR(255) NOT NULL,
#         recipient_phone VARCHAR(10) NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )   
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS api_details (
#         id SERIAL PRIMARY KEY,
#         user_id INT REFERENCES users(id) NOT NULL,
#         api_key VARCHAR(255) NOT NULL,
#         api_limit INT NOT NULL,
#         validity TIMESTAMP NOT NULL,
#         is_active BOOLEAN DEFAULT TRUE,
#         is_email_api BOOLEAN DEFAULT FALSE,
#         is_sms_api BOOLEAN DEFAULT FALSE,
#         is_whatsapp_api BOOLEAN DEFAULT FALSE,
#         is_push_notification_api BOOLEAN DEFAULT FALSE,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS subscription (
#         id SERIAL PRIMARY KEY,
#         subscription_plan VARCHAR(255) NOT NULL,
#         subscription_amount INT NOT NULL,
#         subscription_validity TIMESTAMP NOT NULL,
#         subscription_description VARCHAR(255) NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS user_subscription (
#         id SERIAL PRIMARY KEY,
#         user_id INT REFERENCES users(id) NOT NULL,
#         subscription_id INT REFERENCES users(id) NOT NULL,
#         subscription_start_date TIMESTAMP NOT NULL,
#         subscription_end_date TIMESTAMP NOT NULL,
#         subscription_status VARCHAR(255) DEFAULT 'active',
#         amount_paid INT NOT NULL,
#         used_services INT DEFAULT 0,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS history (
#         id SERIAL PRIMARY KEY,
#         user_id INT REFERENCES users(id) NOT NULL,
#         recipient_id INT REFERENCES users(id) NOT NULL,
#         message TEXT NOT NULL,
#         status VARCHAR(255) NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS template (
#         id SERIAL PRIMARY KEY,
#         user_id INT REFERENCES users(id) NOT NULL,
#         template_name VARCHAR(255) NOT NULL,
#         message TEXT NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)

conn.commit()

# Print the connection if successful with if else condition
if conn:
    print("Database connected successfully")
else:
    print("Database not connected successfully")

# def show_tables():
#     cur.execute("""
#         SELECT table_name
#         FROM information_schema.tables
#         WHERE table_schema = 'public'
#     """)
#     tables = cur.fetchall()
#     for table in tables:
#         print(table[0])

# show_tables()

# Function to send email
def send_email(to_email, subject, message):
    print("Sending email...")
    from_email = os.getenv('EMAIL')
    password = os.getenv('EMAIL_PASSWORD')
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()
    print("Email sent successfully")

# Function to enqueue email sending
def enqueue_email(to_email, subject, message):
    job = q.enqueue_call(
        func=send_email, args=(to_email, subject, message), result_ttl=5000
    )
    print(f"Task ({job.id}) added to the queue")

# Function to send sms fastsms api
def send_sms(phone, otp):
    try:    
        url = "https://www.fast2sms.com/dev/bulkV2"
        querystring = {"authorization":os.getenv('FAST2SMS_API_KEY'),"variables_values":otp,"route":"otp","numbers":phone}
        headers = {
            'cache-control': "no-cache"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
    except Exception as e:
        print(e)

# Function to enqueue sms sending
def enqueue_sms(phone, otp):
    job = q.enqueue_call(
        func=send_sms, args=(phone, otp), result_ttl=5000
    )
    print(f"Task ({job.id}) added to the queue")