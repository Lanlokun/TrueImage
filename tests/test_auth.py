import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_register_user(app):
    with app.app_context():
        user = User(phone_number='1234567890', password_hash='hash')
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(phone_number='1234567890').first() is not None