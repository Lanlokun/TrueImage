from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.services.auth_service import register_user, authenticate_user
from cryptography.hazmat.primitives import serialization
from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.asymmetric import rsa

auth_bp = Blueprint('auth', __name__)

from app.models import User
from app.extensions import db

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Serialize keys to bytes
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




@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form['phone']
        if User.query.filter_by(phone_number=phone_number).first():
            flash('Phone number already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        password = request.form['password']

        # Generate keys
        private_pem, public_pem = generate_keys()

        # Create user
        user = User(
            phone_number=phone_number,
            password_hash=generate_password_hash(password),
            private_key=private_pem,  # Store private key
            public_key=public_pem     # Store public key
        )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone']
        password = request.form['password']
        user = authenticate_user(phone_number, password)
        if user:
            login_user(user)
            return redirect(url_for('images.upload_image'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))