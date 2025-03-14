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
    verification_result = None  # Reset the verification result

    if request.method == 'POST' and 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        # Save and sign the image
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        signature, image_hash = sign_image(current_user.id, filepath)
        if signature is None:
            flash('Error signing image.', 'danger')
            return redirect(request.url)

        flash('Image signed successfully.', 'success')
        return redirect(url_for('images.upload_image'))

    return render_template('upload_image.html', verification_result=verification_result)


@images_bp.route('/verify_image', methods=['POST'])
@login_required
def verify_image_route():
    verification_result = None

    if 'verify_image' in request.files:
        verify_file = request.files['verify_image']
        if verify_file.filename == '':
            flash('No file selected for verification.', 'warning')
            return redirect(url_for('images.upload_image'))

        # Save and verify the image
        verify_filename = secure_filename(verify_file.filename)
        verify_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], verify_filename)
        verify_file.save(verify_filepath)

        # Call the verify_image function and store the result
        verification_result = verify_image(current_user.id, verify_filepath)

        if verification_result is None:
            flash('Error verifying image.', 'danger')
        elif verification_result:
            flash('✅ Image verified successfully.', 'success')
        else:
            flash('❌ Invalid image signature.', 'danger')

    return redirect(url_for('images.upload_image', verification_result=verification_result))
