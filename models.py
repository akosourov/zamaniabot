from app import app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean())

    def __repr__(self):
        return '<User: {} {} {} {} {}>'.format(self.id, self.first_name,
                                               self.last_name, self.username,
                                               self.is_admin)


class FeedBack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_incomplete = db.Column(db.Boolean)

    def __repr__(self):
        return '<FeedBack: {}...>'.format(self.text[:20] if self.text else '')
