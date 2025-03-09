from app.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):  # Inherit from UserMixin
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    private_key = db.Column(db.LargeBinary, nullable=False)
    public_key = db.Column(db.LargeBinary, nullable=False)

    # Flask-Login required properties and methods
    @property
    def is_active(self):
        # Return True if the user is active, False otherwise
        # You can customize this logic based on your application's requirements
        return True

    @property
    def is_authenticated(self):
        # Return True if the user is authenticated
        return True

    @property
    def is_anonymous(self):
        # Return False for regular users
        return False

    def get_id(self):
        # Return the user's unique identifier (usually the user's ID)
        return str(self.id)

class ImageMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    image_hash = db.Column(db.String(64), nullable=False)
    signature = db.Column(db.LargeBinary, nullable=False)
