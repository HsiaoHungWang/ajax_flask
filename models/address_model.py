from . import db

class Address(db.Model):
    __tablename__ = 'address'

    Id = db.Column(db.Integer, primary_key=True)
    City = db.Column(db.Text)
    Site_Id = db.Column(db.Text)
    Road = db.Column(db.Text)
