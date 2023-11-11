from flask_login import UserMixin, login_user,logout_user
from db import *
class Message(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    data=db.Column(db.String(200),nullable=False)

    def __repr__(self):
        return '<Message %r' % self.id
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name= db.Column(db.String(50), nullable=False)
    second_name= db.Column(db.String(50), nullable=False)
    third_name = db.Column(db.String(50), nullable=False)
    is_student= db.Column(db.Boolean, default=True)
    cur_group_or_dep=db.Column(db.String(50), nullable=False)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

class Courseworks(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200), primary_key=False)
    #data = db.Column(db.String(200),primary_key=False)
    group = db.Column(db.String(200),primary_key=False)
    departament = db.Column(db.String(200), primary_key=False)
    student = db.Column(db.String(200), primary_key=False)
    studentName = db.Column(db.String(200), primary_key=False)
    tutor_name = db.Column(db.String(200), primary_key=False)
    tutor_status = db.Column(db.String(200), primary_key=False)
    tutor_rank = db.Column(db.String(200), primary_key=False)
    tutor_pos = db.Column(db.String(200), primary_key=False)
    year = db.Column(db.Integer,primary_key=False)
    link = db.Column(db.String(200), primary_key=False)
    def __repr__(self):
        return '<Message %r' % self.id