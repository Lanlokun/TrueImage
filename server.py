from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from PIL import Image
import pickle  # Add pickle import


app = Flask(__name__)

# Secret key for session management
app.secret_key = os.urandom(24)

# Define folders
UPLOAD_FOLDER = 'uploads'
KEYS_FOLDER = 'keys'
ENCRYPTED_FOLDER = 'encrypted_images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENCRYPTED_FOLDER'] = ENCRYPTED_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KEYS_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENCRYPTED_FOLDER'] = ENCRYPTED_FOLDER

# Generate RSA keys
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

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form['phone']
        id_card = request.form['id_card']

        private_pem, public_pem = generate_keys()

        user_dir = os.path.join(KEYS_FOLDER, phone_number)
        os.makedirs(user_dir, exist_ok=True)

        # Save keys
        with open(os.path.join(user_dir, 'private_key.pem'), 'wb') as private_file:
            private_file.write(private_pem)

        with open(os.path.join(user_dir, 'public_key.pem'), 'wb') as public_file:
            public_file.write(public_pem)

        # Store the phone number in session
        session['phone_number'] = phone_number

        return redirect(url_for('upload_image'))
    
    return render_template('register.html')

import hashlib

def generate_image_hash(image_path):
    """Generates a SHA-256 hash of the image file."""
    sha256_hash = hashlib.sha256()
    
    with open(image_path, "rb") as f:
        # Read the image file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    verification_result = None
    phone_number = session.get('phone_number')

    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            logging.debug(f"Image saved at {filepath}")

            # Sign the image
            try:
                signature, image_hash, signature_filename = sign_image(phone_number, filepath)
                if signature is None:
                    return render_template('upload_image.html', message="Error signing image.")

                logging.debug(f"Image signed successfully: {signature}")

                # Provide a download link for the signature file
                signature_url = url_for('download_signature', filename=signature_filename)
                return render_template('upload_image.html', message="Image signed successfully.", download_link=signature_url)

            except Exception as e:
                logging.error(f"Signing failed: {e}")
                return render_template('upload_image.html', message="Error signing image.")

        elif 'encrypted_image' in request.files:
            file = request.files['encrypted_image']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Locate the metadata file based on the original image's filename
            original_filename = filename.replace(".signed", "")  # Remove .signed if present
            metadata_filename = original_filename + ".meta"
            metadata_path = os.path.join(app.config['ENCRYPTED_FOLDER'], metadata_filename)

            try:
                with open(metadata_path, "rb") as meta_file:
                    metadata = pickle.load(meta_file)

                signature = metadata['signature']
                image_hash = metadata['image_hash']

                verification_result = verify_image(phone_number, filepath, signature)
                logging.debug(f"Verification result: {verification_result}")

            except FileNotFoundError:
                verification_result = "Metadata not found for this image."
                logging.error("Metadata file not found.")

            return render_template('upload_image.html', verification=verification_result)

    return render_template('upload_image.html', phone_number=phone_number, verification=verification_result)

@app.route('/download_signature/<filename>')
def download_signature(filename):
    return send_from_directory(app.config['ENCRYPTED_FOLDER'], filename, as_attachment=True)# Hash image


def hash_image(image_path):
    with open(image_path, 'rb') as img_file:
        image_bytes = img_file.read()
    return hashlib.sha256(image_bytes).hexdigest()

# Encrypt image using public key
def sign_image(phone_number, image_path):
    try:
        private_key_path = os.path.join(KEYS_FOLDER, phone_number, 'private_key.pem')
        logging.debug(f"Loading private key from {private_key_path}")

        with open(private_key_path, 'rb') as private_file:
            private_key = serialization.load_pem_private_key(
                private_file.read(),
                password=None
            )

        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        image_hash = hashlib.sha256(image_data).digest()

        signature = private_key.sign(
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Save the signature as a .sig file
        original_filename = os.path.basename(image_path)
        signature_filename = original_filename + ".sig"  # Append .sig to the original filename
        signature_path = os.path.join(app.config['ENCRYPTED_FOLDER'], signature_filename)
        with open(signature_path, 'wb') as sig_file:
            sig_file.write(signature)

        # Save the metadata with the same base name as the original image
        metadata = {'image_hash': image_hash, 'signature': signature}
        metadata_filename = original_filename + ".meta"  # Match the original image filename
        metadata_path = os.path.join(app.config['ENCRYPTED_FOLDER'], metadata_filename)

        with open(metadata_path, "wb") as meta_file:
            pickle.dump(metadata, meta_file)

        logging.debug(f"Signature saved at {signature_path}")
        logging.debug(f"Metadata saved at {metadata_path}")
        return signature, image_hash, signature_filename

    except Exception as e:
        logging.error(f"Error in signing image: {e}")
        return None, None, None

@app.route('/download_decrypted_image/<filename>')
def download_decrypted_image(filename):
    # Load the private key
    phone_number = session.get('phone_number')
    private_key_path = os.path.join(KEYS_FOLDER, phone_number, 'private_key.pem')
    with open(private_key_path, 'rb') as private_file:
        private_key = serialization.load_pem_private_key(private_file.read(), password=None)

    # Load the encrypted image
    encrypted_image_path = os.path.join(app.config['ENCRYPTED_FOLDER'], filename)
    with open(encrypted_image_path, 'rb') as enc_file:
        encrypted_data = enc_file.read()

    # Decrypt the image
    decrypted_image = decrypt_image(private_key, encrypted_data)

    # Save the decrypted image in a temporary location for downloading
    decrypted_image_filename = filename.replace(".enc", "_decrypted.png")
    decrypted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_image_filename)
    with open(decrypted_image_path, 'wb') as dec_file:
        dec_file.write(decrypted_image)

    # Send the decrypted image for download
    return send_from_directory(app.config['UPLOAD_FOLDER'], decrypted_image_filename)

def verify_image(phone_number, image_path, signature):
    # Load the public key from the user's folder
    public_key_path = os.path.join(KEYS_FOLDER, phone_number, 'public_key.pem')
    with open(public_key_path, 'rb') as public_file:
        public_key = serialization.load_pem_public_key(public_file.read())

    # Read the image file
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Recalculate the SHA-256 hash
    image_hash = hashlib.sha256(image_data).digest()

    try:
        # Verify the signature
        public_key.verify(
            signature,
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return "Signature is valid. Image is authentic."
    except Exception as e:
        return f"Signature verification failed: {e}"

# Decrypt image
def decrypt_image(private_key, encrypted_aes_key, iv, encrypted_image):
    # Ensure encrypted_image is a byte-like object
    if isinstance(encrypted_image, str):
        encrypted_image = encrypted_image.encode('utf-8')

    # Decrypt AES key with RSA
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt image with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_padded_image = decryptor.update(encrypted_image) + decryptor.finalize()

    # Unpadding after decryption
    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_image = unpadder.update(decrypted_padded_image) + unpadder.finalize()

    return decrypted_image

# Assuming the `verify_image` function is updated and imported correctly
if __name__ == '__main__':
    app.run(debug=True)
