from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.services.image_service import sign_image, verify_image
from app.config import Config
import logging

images_bp = Blueprint('images', __name__)

@images_bp.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    verification_result = None
    signature_filename = None
    
    if request.method == 'POST':
        # Handle Image Upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                flash('No file selected.')
                return redirect(request.url)

            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logging.debug(f"File saved to: {filepath}")

            # Sign the image
            signature, image_hash = sign_image(current_user.id, filepath)
            if signature is None:
                flash('Error signing image.')
                return redirect(request.url)

            flash('Image signed successfully.')
            signature_filename = f"{filename}.sig"
            return redirect(url_for('images.upload_image'))

        # Handle Image Verification
        elif 'verify_image' in request.files:
            verify_file = request.files['verify_image']
            if verify_file.filename == '':
                flash('No file selected for verification.')
                return redirect(request.url)

            # Save the verification file
            verify_filename = secure_filename(verify_file.filename)
            verify_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], verify_filename)
            verify_file.save(verify_filepath)
            logging.debug(f"File for verification saved to: {verify_filepath}")

            # Verify the image
            verification_result = verify_image(current_user.id, verify_filepath)

            if verification_result is None:
                flash('Error verifying image.')
            elif verification_result:
                flash('Image verified successfully.')
            else:
                flash('Invalid image signature.')

    return render_template('upload_image.html', verification_result=verification_result, signature_filename=signature_filename)