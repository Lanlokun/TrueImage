import os
import hashlib
import logging
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from app.models import ImageMetadata, User
from app.extensions import db

logging.basicConfig(level=logging.DEBUG)

def sign_image(user_id, image_path):
    try:
        # Load image
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Hash the image with SHA-256 (as bytes)
        image_hash = hashlib.sha256(image_data).digest()

        # Load user
        user = User.query.get(user_id)
        if not user:
            logging.error("User not found")
            return False

        # Load private key
        private_key = serialization.load_pem_private_key(
            user.private_key,
            password=None,
        )

        # Sign the hash
        signature = private_key.sign(
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encode signature in base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')

        # Store metadata
        metadata = ImageMetadata(
            user_id=user.id,
            filename=os.path.basename(image_path),
            image_hash=hashlib.sha256(image_data).hexdigest(),  # Store as string
            signature=signature_b64  # Store as base64 string
        )
        db.session.add(metadata)
        db.session.commit()

        logging.info("Image signed and metadata saved.")
        return True

    except Exception as e:
        logging.error(f"Error signing image: {e}")
        return False


def verify_image(user_id, image_path):
    try:
        # Load image
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Recompute hash
        image_hash = hashlib.sha256(image_data).digest()

        # Get metadata
        metadata = ImageMetadata.query.filter_by(
            user_id=user_id,
            filename=os.path.basename(image_path)
        ).first()

        # Get user and public key
        user = User.query.get(user_id)
        if not user:
            logging.error("User not found")
            return False

        public_key = serialization.load_pem_public_key(user.public_key)

        # Decode the base64 signature
        signature_bytes = base64.b64decode(metadata.signature)

        # Verify signature
        public_key.verify(
            signature_bytes,
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        logging.info("Signature is valid.")
        return True

    except Exception as e:
        logging.error(f"Error verifying image: {e}")
        return False
