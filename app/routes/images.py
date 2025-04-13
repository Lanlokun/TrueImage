from flask import Blueprint, request, jsonify, send_from_directory, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import jwt
from functools import wraps
from app.models import User, ImageMetadata

import logging

from app.services.image_service import sign_image, verify_image

images_bp = Blueprint('images', __name__)


secret_key = os.getenv("SECRET_KEY")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            token = token.split("Bearer ")[-1]  # Extract JWT from "Bearer <token>"
            decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            # Fetch the user from the database
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found!"}), 401

            # Set current_user manually
            setattr(current_app, 'current_user', user)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated



@images_bp.route('/upload', methods=['POST'])
@jwt_required  # Use the JWT authentication decorator
def upload_image():
    user = getattr(current_app, 'current_user', None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Check if the file part exists in the request
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['image']
    
    # Check if the file has no filename
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Validate the file extension
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed."}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)

    # Check if the file already exists
    if os.path.exists(filepath):
        return jsonify({"error": "An image with this name already exists. Please rename your file."}), 409


    try:
        # Save the file
        file.save(filepath)

        # Sign the image and get the metadata (adjust to handle return values properly)
        success = sign_image(user.id, filepath)  # Assume sign_image returns a boolean

        if not success:  # If signing failed, handle gracefully
            return jsonify({"error": "Error signing image"}), 500

        # Return success message with file URL
        return jsonify({
            "message": "Image uploaded successfully",
            "filename": filename,
            "url": url_for('images.get_image', filename=filename, _external=True)
        })

    except Exception as e:
        # Log any errors
        logging.error(f"Error saving file: {str(e)}")
        return jsonify({"error": "An error occurred while uploading the image"}), 500


@images_bp.route('/verify', methods=['POST'])
@jwt_required
def verify_image_route():
    user = getattr(current_app, 'current_user', None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Ensure 'image' is the correct key
    if 'image' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    verify_file = request.files['image']

    if verify_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(verify_file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        verify_filename = secure_filename(verify_file.filename)
        verify_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], verify_filename)
        verify_file.save(verify_filepath)

        verification_result = verify_image(user.id, verify_filepath)

        # Fetch Image Metadata
        metadata = ImageMetadata.query.filter_by(user_id=user.id, filename=verify_filename).first()

        # Handle image tampering or verification failure
        if verification_result is False:
            return jsonify({
                "verified": False,
                "error": "Image tampered or verification failed.",
                "details": "The image might have been altered or doesn't match expected patterns."
            }), 400

        # If image is successfully verified
        uploader_info = {
            "phone_number": user.phone_number,
            "verified": verification_result
        }

        image_metadata = {
            "filename": metadata.filename,
            "uploaded_at": metadata.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify({
            "verified": verification_result,
            "uploader": uploader_info,
            "image_metadata": image_metadata
        })

    except Exception as e:
        logging.error(f"Error verifying image: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@images_bp.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@images_bp.route('/gallery', methods=['GET'])
@jwt_required
def gallery():
    try:
        image_records = ImageMetadata.query.all()
        images = []

        for image in image_records:
            images.append({
                "filename": image.filename,
                "url": url_for('images.get_image', filename=image.filename, _external=True),
                "uploaded_at": image.uploaded_at.isoformat(),
                "uploader_id": image.user_id,
                "uploader_phone": image.user.phone_number,  # Assuming phone number is safe to show
            })

        return jsonify({"images": images})

    except Exception as e:
        logging.error(f"Error loading gallery: {str(e)}")
        return jsonify({"error": "An error occurred while loading the gallery"}), 500

@images_bp.route('/delete', methods=['DELETE'])
@jwt_required
def delete_image():
    data = request.get_json()
    image_filename = data.get('image')

    if not image_filename:
        return jsonify({"error": "No image specified for deletion"}), 400

    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(image_filename))

    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            return jsonify({"message": "Image deleted successfully"})
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting image: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the image"}), 500
