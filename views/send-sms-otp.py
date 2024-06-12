# Function to send sms fastsms api
import os
import random
import requests
from rq import Queue, Connection, Worker
import redis
REDIS_URL = os.getenv('REDIS_URL')
redisconn = redis.from_url(REDIS_URL)

if __name__ == '__main__':
    with Connection(redisconn):
        worker = Worker(map(Queue, ['default']))
        worker.work()
q = Queue(connection=redisconn)
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
def enqueue_sms(phone, otp):
    job = q.enqueue_call(
        func=send_sms, args=(phone, otp), result_ttl=5000
    )
    print(f"Task ({job.id}) added to the queue")