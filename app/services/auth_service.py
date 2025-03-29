from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

def register_user(phone_number, password):
    """Registers a new user with a hashed password."""
    try:
        # Check if user already exists
        if User.query.filter_by(phone_number=phone_number).first():
            return {"error": "Phone number already registered"}, 400

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create user instance
        user = User(phone_number=phone_number, password_hash=password_hash)

        # Save to DB
        db.session.add(user)
        db.session.commit()
        
        return {"message": "User registered successfully"}, 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Database error", "details": str(e)}, 500

def authenticate_user(phone_number, password):
    """Authenticates a user by checking the hashed password."""
    try:
        # Fetch the user object based on the phone number
        user = User.query.filter_by(phone_number=phone_number).first()
        
        # If the user is found and the password hash matches
        if user and check_password_hash(user.password_hash, password):
            return user  # Return the User object directly
        
        # If the credentials are invalid, return None
        return None
    except SQLAlchemyError as e:
        return {"error": "Database error", "details": str(e)}, 500
