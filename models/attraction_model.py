from . import db

class Attraction(db.Model):
    __tablename__ = 'attractions'

    AttractionID = db.Column(db.String(50), primary_key=True)
    AttractionName = db.Column(db.String(200))
    Description = db.Column(db.Text)
    PositionLat = db.Column(db.Float)
    PositionLon = db.Column(db.Float)
    City = db.Column(db.String(20))
    Town = db.Column(db.String(20))
    ZipCode = db.Column(db.String(10))
    StreetAddress = db.Column(db.String(300))
    TrafficInfo = db.Column(db.Text)
    ParkingInfo = db.Column(db.Text)
    WebsiteURL = db.Column(db.String(300))
    Tags = db.Column(db.String(300))
    IsPublicAccess = db.Column(db.Boolean)
    IsAccessibleForFree = db.Column(db.Boolean)
    UpdateTime = db.Column(db.String(30))


class AttractionImage(db.Model):
    __tablename__ = 'attraction_images'

    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(db.String(50), db.ForeignKey('attractions.AttractionID'))
    Name = db.Column(db.String(200))
    Description = db.Column(db.String(300))
    URL = db.Column(db.String(500))
