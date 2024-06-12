from datetime import datetime
from app import db

class BlacklistedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_status = db.Column(db.String(255), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sms_otp = db.Column(db.String(255), nullable=False)
    email_otp = db.Column(db.String(255), nullable=False)
    sms_otp_status = db.Column(db.String(255), default='pending')
    email_otp_status = db.Column(db.String(255), default='pending')
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

class RecipientData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_name = db.Column(db.String(255), nullable=False)
    recipient_email = db.Column(db.String(255), nullable=False)
    recipient_phone = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

class ApiDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)
    api_limit = db.Column(db.Integer, nullable=False)
    validity = db.Column(db.TIMESTAMP, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_email_api = db.Column(db.Boolean, default=False)
    is_sms_api = db.Column(db.Boolean, default=False)
    is_whatsapp_api = db.Column(db.Boolean, default=False)
    is_push_notification_api = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_plan = db.Column(db.String(255), nullable=False)
    subscription_amount = db.Column(db.Integer, nullable=False)
    subscription_validity = db.Column(db.TIMESTAMP, nullable=False)
    subscription_description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

class UserSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    subscription_start_date = db.Column(db.TIMESTAMP, nullable=False)
    subscription_end_date = db.Column(db.TIMESTAMP, nullable=False)
    subscription_status = db.Column(db.String(255), default='active')
    amount_paid = db.Column(db.Integer, nullable=False)
    used_services = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template_name = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)