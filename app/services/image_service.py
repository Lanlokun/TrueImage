import os
import hashlib
import logging
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from app.models import ImageMetadata
from app.extensions import db
from app.models import User
from datetime import datetime
import base64

logging.basicConfig(level=logging.DEBUG)

def sign_image(user_id, image_path):
    try:
        # Read the image file
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        # Compute the image hash
        image_hash = hashlib.sha256(image_data).digest()

        # Retrieve the user's private key
        user = User.query.get(user_id)
        if not user:
            logging.error(f"User not found for user_id={user_id}")
            return None, None

        private_key = serialization.load_pem_private_key(
            user.private_key,
            password=None
        )

        # Sign the image hash
        signature = private_key.sign(
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Save the metadata to the database
        metadata = ImageMetadata(
            user_id=user_id,
            filename=os.path.basename(image_path),
            image_hash=image_hash.hex(),  # Store the image hash as a hex string
            signature=signature,
        )
        db.session.add(metadata)
        db.session.commit()
        logging.debug(f"Metadata saved for user_id={user_id}, filename={os.path.basename(image_path)}")

        return signature, image_hash

    except Exception as e:
        logging.error(f"Error signing image: {e}")
        return None, None

def verify_image(user_id, image_path):
    try:

        # Read the image file
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        # Compute the image hash
        image_hash = hashlib.sha256(image_data).digest()

        # Load the metadata from the database
        metadata = ImageMetadata.query.filter_by(
            user_id=user_id,
            filename=os.path.basename(image_path)
        ).first()

        if not metadata:
            logging.error(f"No metadata found for user_id={user_id}, filename={os.path.basename(image_path)}")
            return False  # Return False when metadata is not found

        # Retrieve the user from the database
        user = User.query.get(user_id)
        if not user:
            logging.error(f"User not found for user_id={user_id}")
            return False  # Return False when user is not found

        # Load the public key from the database
        public_key = serialization.load_pem_public_key(
            user.public_key  # Public key stored in the User table
        )

        # Verify the signature
        public_key.verify(
            metadata.signature,
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        logging.debug("Signature is valid. Image is authentic.")
        return True  # Return True when the signature is valid

    except Exception as e:
        logging.error(f"Error verifying image: {e}")
        return False  # Return False when an error occurs
