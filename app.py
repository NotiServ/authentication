import json
import random
from flask import Flask, request
from flask_restful import Api, Resource
from config import enqueue_email, cur, enqueue_sms

app = Flask(__name__)
api = Api(app)

class Home(Resource):
    def get(self):
        return {'message': 'Welcome to the home page!'}

class Register(Resource):
    def post(self):
        try:
            # Get JSON data
            data = request.get_json()
            if not data['username'] or not data['email'] or not data['phone'] or not data['password'] or not data['confirm_password']:
                return {'message': 'All fields are required'}
            username = data['username']
            email = data['email']
            phone = data['phone']
            password = data['password']
            confirm_password = data['confirm_password']

            if not username or not email or not phone or not password or not confirm_password:
                return {'message': 'All fields are required'}
            elif password != confirm_password:
                return {'message': 'Passwords do not match'}
            elif len(password) < 7:
                return {'message': 'Password must be at least 6 characters long'}
            
            elif len(phone) != 10:
                return {'message': 'Phone number must be 10 digits long'}
            
            elif not email.endswith('@gmail.com'):
                return {'message': 'Email must be a Gmail account'}
            
            elif not username.isalnum():
                return {'message': 'Username must be alphanumeric'}
            
            elif not phone.isdigit():
                return {'message': 'Phone number must be numeric'}
            
            # elif not email.isalnum():
            #     return {'message': 'Email must be alphanumeric'}
            
            # elif not password.isalnum():
            #     return {'message': 'Password must be alphanumeric'}
            
            # elif not confirm_password.isalnum():
            #     return {'message': 'Confirm password must be alphanumeric'}
            
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return {'message': 'Email already exists'}
            
            cur.execute("SELECT * FROM users WHERE phone = %s", (phone,))
            if cur.fetchone():
                return {'message': 'Phone number already exists'}
            
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return {'message': 'Username already exists'}
            
            cur.execute("INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)", (username, email, phone, password))

            # Generate OTPs
            email_otp=random.randint(100000,999999)
            sms_otp=random.randint(100000,999999)

            # Send OTPs 
            enqueue_email(email, 'OTP for email verification', f'Your OTP for email verification is {email_otp}')
            enqueue_sms(phone, sms_otp)

            #  Save OTPs in the database
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user_id = cur.fetchone()[0]
            cur.execute("INSERT INTO verification (user_id, sms_otp, email_otp) VALUES (%s, %s, %s)", (user_id, sms_otp, email_otp))
            return {'message': 'Registration successful'}
        except Exception as e:
            return {'error': str(e)}
        
class DeleteUser(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data['email']
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if not cur.fetchone():
                return {'message': 'Email does not exist'}
            cur.execute("DELETE FROM users WHERE email = %s", (email,))
            return {'message': 'User deleted successfully'}
        except Exception as e:
            return {'error': str(e)}

class GetAllUsers(Resource):
    def get(self):
        try:
            print(cur.execute("SELECT * FROM users"))
            users = cur.fetchall()
            print(users)
            # print(json.dumps(users))
            return {'users': users}
        except Exception as e:
            return {'error': str(e)}

api.add_resource(Home, '/')
api.add_resource(GetAllUsers, '/users')
api.add_resource(Register, '/register')
api.add_resource(DeleteUser, '/delete')

if __name__ == '__main__':
    app.run(debug=True)