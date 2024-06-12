import random
import re
from flask import Blueprint, request, jsonify
from models.models import User, BlacklistedToken
from app import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from .tasks import send_email, send_sms
from views.decorators import blacklist_token, check_blacklist

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "User already exists with this email"}), 400
        if User.query.filter_by(phone=phone).first():
            return jsonify({"message": "User already exists with this phone number"}), 400
        if len(password) < 8:
            return jsonify({"message": "Password must be at least 8 characters long"}), 400

        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_regex, password):
            return jsonify({"message": "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character"}), 400

        if password != confirm_password:
            return jsonify({"message": "Passwords do not match"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, phone=phone, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity={'username': user.username, 'email': user.email})
            # blacklisted_token = BlacklistedToken(token=access_token)
            
            #     # insert the token
            # db.session.add(blacklisted_token)
            # db.session.commit()
            return jsonify({"message":"Login Successfully.", "email":user.email  ,"token": access_token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_blueprint.route('/logout', methods=['POST'])
@jwt_required()
@check_blacklist
@blacklist_token
def logout():
    return jsonify({"message": "Logout successful"}), 200

@auth_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        otp=random.randint(100000,999999)
        send_email.delay(email, "Reset Password OTP", f"Your OTP is {otp}")
        return jsonify({"message": "Reset password OTP sent to your email"}), 200

    return jsonify({"message": "User not found"}), 404

@auth_blueprint.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    user = User.query.filter_by(email=email).first()
    if user:
        # Call a function to verify OTP
        if new_password != confirm_password:
            return jsonify({"message": "Passwords do not match"}), 400

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return jsonify({"message": "Password reset successfully"}), 200

    return jsonify({"message": "User not found"}), 404

@auth_blueprint.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, old_password):
        if len(new_password) < 8:
            return jsonify({"message": "Password must be at least 8 characters long"}), 400
        special_chars = ['$', '@', '#', '%', '!', '^', '&', '*']
        if not any(char.isupper() for char in new_password):
            return jsonify({"message": "Password must contain at least one uppercase letter"}), 400
        if not any(char.islower() for char in new_password):
            return jsonify({"message": "Password must contain at least one lowercase letter"}), 400
        if not any(char.isdigit() for char in new_password):
            return jsonify({"message": "Password must contain at least one digit"}), 400
        if not any(char in special_chars for char in new_password):
            return jsonify({"message": "Password must contain at least one special character"}), 400
        if new_password != confirm_password:
            return jsonify({"message": "New Passwords and Confirm Password not matched"}), 400
        if old_password == new_password:
            return jsonify({"message": "New password cannot be the same as old password"}), 400

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200

    return jsonify({"message": "Invalid credentials"}), 401

@auth_blueprint.route('/delete-account', methods=['POST'])
@jwt_required()
@check_blacklist
# @blacklist_token
def delete_account():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            db.session.delete(user)
            db.session.commit()
            jti = get_jwt()['jti']
            blacklisted_token = BlacklistedToken(token=jti)
            db.session.add(blacklisted_token)
            db.session.commit()
            return jsonify({"message": "Account deleted successfully"}), 200

        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_blueprint.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    # Call a function to verify OTP
    return jsonify({"message": "Email verified successfully"}), 200

@auth_blueprint.route('/verify-phone', methods=['POST'])
def verify_phone():
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')

    # Call a function to verify OTP
    return jsonify({"message": "Phone verified successfully"}), 200

@auth_blueprint.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')

    # Call a function to resend OTP
    return jsonify({"message": "OTP resent successfully"}), 200

@auth_blueprint.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    phone = data.get('phone')

    user = User.query.filter_by(email=email).first()
    if user:
        user.username = username
        user.phone = phone
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    return jsonify({"message": "User not found"}), 404

@auth_blueprint.route('/get-profile', methods=['POST'])
def get_profile():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"username": user.username, "email": user.email, "phone": user.phone}), 200

    return jsonify({"message": "User not found"}), 404


@auth_blueprint.route('/get-all-users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({"username": user.username, "email": user.email, "phone": user.phone})
    return jsonify(user_list), 200


# get all tokens
@auth_blueprint.route('/get-all-tokens', methods=['GET'])
@jwt_required()
@check_blacklist
def get_all_tokens():
    tokens = BlacklistedToken.query.all()
    token_list = []
    for token in tokens:
        token_list.append({"token": token.token})
    return jsonify(token_list), 200