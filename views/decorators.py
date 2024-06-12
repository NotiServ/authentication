from functools import wraps
from flask_jwt_extended import get_jwt
from models.models import BlacklistedToken, db
from flask import jsonify

def blacklist_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jti = get_jwt()['jti']
        blacklisted_token = BlacklistedToken(token=jti)
        try:
            db.session.add(blacklisted_token)
            db.session.commit()
        except Exception as e:
            return jsonify({"message": str(e)}), 500
        return f(*args, **kwargs)
    return decorated



def check_blacklist(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jti = get_jwt()['jti']
        blacklisted_token = BlacklistedToken.query.filter_by(token=jti).first()
        if blacklisted_token:
            return jsonify({"message": "Invalid token or token is expired"}), 401
        return f(*args, **kwargs)
    return decorated