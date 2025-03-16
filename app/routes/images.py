from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.services.image_service import sign_image, verify_image
from app.config import Config
import logging

images_bp = Blueprint('images', __name__)
from flask import current_app, request, flash, redirect, render_template, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

@images_bp.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    verification_result = None
    uploaded_image = None

    if request.method == 'POST' and 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        # Secure and create the filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Check if the file already exists
        if os.path.exists(filepath):
            flash('Image with this filename already exists. Please upload a different image.', 'danger')
            return redirect(request.url)

        # Save and sign the image
        file.save(filepath)

        # Sign the image (assumes sign_image is defined elsewhere)
        signature, image_hash = sign_image(current_user.id, filepath)
        if signature is None:
            flash('Error signing image.', 'danger')
            return redirect(request.url)

        flash('Image signed successfully.', 'success')

        # After saving the file, pass the uploaded image URL for preview
        uploaded_image = url_for('images.uploaded_file', filename=filename)  # Adjusted to use the new route
        print(uploaded_image)

        return render_template('upload_image.html', verification_result=verification_result, uploaded_image=uploaded_image)

    return render_template('upload_image.html', verification_result=verification_result, uploaded_image=uploaded_image)


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



@images_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@images_bp.route('/gallery')
@login_required
def gallery():
    images = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    for filename in os.listdir(upload_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):  # Filter image file extensions
            images.append(url_for('images.uploaded_file', filename=filename))  # Add the URL to the image
    
    return render_template('image_gallery.html', images=images)


@images_bp.route('/delete_image', methods=['GET'])
@login_required
def delete_image():
    image_path = request.args.get('image')
    filename = os.path.basename(image_path)
    image_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        os.remove(image_full_path)  # Delete the image file
        flash('Image deleted successfully!', 'success')
    except FileNotFoundError:
        flash('Image not found.', 'danger')

    return redirect(url_for('images.gallery'))
