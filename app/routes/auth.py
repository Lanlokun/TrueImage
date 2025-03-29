from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
from app.services.auth_service import authenticate_user
from cryptography.hazmat.primitives import serialization
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.asymmetric import rsa
from app.models import User
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import jwt
import datetime
from dotenv import load_dotenv
import os


auth_bp = Blueprint('auth', __name__)
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

# Generate RSA Key Pair (private/public keys should be managed securely)
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Extract data
    phone_number = data.get('phone')
    national_id = data.get('national_id')
    password = data.get('password')

    if not phone_number or not national_id or not password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    # Check for existing users
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({"status": "error", "message": "Phone number already registered"}), 400
    if User.query.filter_by(national_id=national_id).first():
        return jsonify({"status": "error", "message": "National ID already registered"}), 400

    try:
        # Generate keys
        private_pem, public_pem = generate_keys()

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create and store user
        user = User(
            phone_number=phone_number,
            national_id=national_id,
            password_hash=password_hash,
            private_key=private_pem,
            public_key=public_pem
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"status": "success", "message": "Registration successful! Please log in."}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone_number = data.get('phone')
    password = data.get('password')

    if not phone_number or not password:
        return jsonify({"status": "error", "message": "Phone and password are required"}), 400

    # Call the authenticate_user function and get the user object
    user = authenticate_user(phone_number, password)
    
    if user:  # If the user object is returned
        try:
            # Generate JWT token
            token = jwt.encode({
                'user_id': user.id,  # Access the 'id' attribute of the user object
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, secret_key, algorithm='HS256')

            # Log the user in (e.g., store in session, etc.)
            login_user(user) 

            return jsonify({"status": "success", "message": "Login successful!", "token": token}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to generate token: {str(e)}"}), 500

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
