from enum import Enum

from flask_login import UserMixin

from util import db


class Role(Enum):
    ADMIN = 'adm'
    MANAGER = 'man'
    OPERATOR = 'op'

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None

    def __str__(self):
        return str(self.value).upper()


class LanguageConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lang = db.Column(db.String(2), unique=True, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    occurrences = db.relationship('Occurrence', backref='user')

    def allowed(self, *roles):
        return self.role in roles

    def __repr__(self):
        return f'<User {self.username}>'
