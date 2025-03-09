from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db

def register_user(phone_number, password):
    password_hash = generate_password_hash(password)
    user = User(phone_number=phone_number, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

def authenticate_user(phone_number, password):
    user = User.query.filter_by(phone_number=phone_number).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None