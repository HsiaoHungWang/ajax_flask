from . import db
class Member(db.Model):
    __tablename__ = 'members'

    MemberId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.Text)
    Email = db.Column(db.Text)
    Age = db.Column(db.Integer)
    FileName = db.Column(db.Text)
    Password = db.Column(db.Text)