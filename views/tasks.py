# Function to send email
import random
import os
import smtplib
from celery import Celery
from celery.schedules import crontab
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from rq import Queue, Connection, Worker
from rq.job import Job
import redis
import requests

# REDIS_URL = os.getenv('REDIS_URL')
redisconn = redis.from_url('redis://127.0.0.1:6379')
q = Queue(connection=redisconn)
app=Celery('tasks', broker='redis://127.0.0.1:6379')
app.conf.enable_utc = False
app.conf.timezone = 'Asia/Kolkata'

@app.task
def send_sms(phone):
    try:    
        sms_otp=random.randint(100000,999999)
        url = "https://www.fast2sms.com/dev/bulkV2"
        querystring = {"authorization":os.getenv('FAST2SMS_API_KEY'),"variables_values":sms_otp,"route":"otp","numbers":phone}
        headers = {
            'cache-control': "no-cache"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
    except Exception as e:
        print(e)

# Function to enqueue sms sending
# def enqueue_sms(phone, otp):
#     job = q.enqueue_call(
#         func=send_sms, args=(phone, otp), result_ttl=5000
#     )
#     print(f"Task ({job.id}) added to the queue")

@app.task
def send_email(to_email, subject, message):
    try:
        print("Sending email...")
        from_email = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
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
    except Exception as e:
        print(e)

# Function to enqueue email sending
# def enqueue_email(to_email, subject, message):
#     email_otp =random.randint(100000,999999)
#     # subject = "Email OTP"
#     # message = f"Your OTP is {email_otp}"
#     job = q.enqueue_call(
#         send_email, args=(to_email, subject, message),
#     )
#     # send_email(to_email, subject, message)
#     print(f"Task ({job.id}) added to the queue")

# enqueue_email('sanketugale683@outlook.com')