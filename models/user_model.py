from . import db

class User(db.Model):
    __tablename__ = 'users'

    UserId = db.Column(db.Integer, primary_key=True, unique=True)
    UserName = db.Column(db.Text, nullable=False)
    UserEmail = db.Column(db.Text, nullable=False)
    UserAge = db.Column(db.Integer)