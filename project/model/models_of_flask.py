from flask import g
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, utils
from sqlalchemy import ARRAY
from flask_security.core import current_user
from flask.ext.security.signals import user_registered
from datetime import datetime
# from run_migration import app, db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)



# Define models
roles_users = db.Table('roles_users', 
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    )


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime(), default=datetime.now)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    user_profile = db.relationship("UserProfile", back_populates="user")
    confirmed = db.Column(db.Boolean(), default=False)


    date_of_birth = db.Column(db.Date())
    phone_number = db.Column(db.String(20),default=None)

    # Added on 25-11-2016
    modified = db.Column(db.DateTime(), default=datetime.now)

    otp = db.relationship("Otp", back_populates="user")

    # Added on 12-11-2016
    token_manager = db.relationship("TokenManager", back_populates="user")


    def verify_password(self, password):
        return utils.verify_password(password, self.password)

    def generate_auth_token(self, expiration = 86400):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        print(self.id)
        return s.dumps({ 'id': self.id })

    @staticmethod
    #  This is a static method, as the user will be known only after the token is decoded.
    def verify_auth_token(token):
        # import pdb
        # pdb.set_trace()
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        print(token)
        return user

    #@staticmethod
    def is_anonymous(self):
        if g.current_user:
            return False

        return True


    def __init__(self, first_name, last_name, account_id, email, password, phone_number, date_of_birth, city_id, confirmed):
        self.first_name = first_name
        self.last_name = last_name
        self.account_id = account_id
        self.email = email
        self.password = utils.encrypt_password(password)
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.confirmed = confirmed


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_title = db.Column(db.String(80))
    profile_picture = db.Column(db.String(255))
    website = db.Column(db.String(255))
    about_me = db.Column(db.Text)
    created = db.Column(db.DateTime(), default=datetime.now)
    modified = db.Column(db.DateTime(), default=datetime.now)

    user = db.relationship("User", back_populates="user_profile")
    user_skills = db.relationship("UserSkills", back_populates="user_profile")
    user_interests = db.relationship("UserInterests", back_populates="user_profile")

    def __init__(self, user_id, job_title, profile_picture, website, about_me):
        self.job_title = job_title
        self.profile_picture = profile_picture
        self.website = website
        self.user_id = user_id
        self.about_me = about_me


# Added on 30-10-2016
class Otp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    otp = db.Column(db.Integer)
    otp_type = db.Column(db.SmallInteger, default=0)
    attempt = db.Column(db.SmallInteger, default=0)
    created = db.Column(db.DateTime(), default=datetime.now)
    modified = db.Column(db.DateTime(), default=datetime.now)

    user = db.relationship("User", back_populates="otp")

    def __init__(self, user_id, otp, otp_type):
        self.user_id = user_id
        self.otp = otp
        self.otp_type = otp_type


# Added on 12-11-2016
class TokenManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime(), default=datetime.now)
    user_type = db.Column(db.SmallInteger, default=0)

    user = db.relationship("User", back_populates="token_manager")

    def __init__(self, user_id, created, user_type=0):
        self.user_id = user_id
        self.created = created
        self.user_type = user_type


# Added on 25-11-2016
class UserHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    email = db.Column(db.String(255))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    card = db.Column(db.String(15), default=None)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=False)
    confirmed = db.Column(db.Boolean(), default=False)
    date_of_birth = db.Column(db.Date())
    conf_credits = db.Column(db.Integer(), default=0)
    phone_number = db.Column(db.String(20), default=0)
    created = db.Column(db.DateTime(), default=datetime.now)
    modified = db.Column(db.DateTime(), default=datetime.now)
    confirmed_at = db.Column(db.DateTime())
    transfer_date = db.Column(db.DateTime(), default=datetime.now)

    # Relationship
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    otp = db.relationship("Otp", back_populates="user")
    token_manager = db.relationship("TokenManager", back_populates="user")


class Reminders(Base):
    """docstring for Reminders"""
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(String(255), default=None)
    execution_time = Column(DateTime)
        

class RemindersHistory(Base):
    """docstring for Reminders history"""
    __tablename__ = 'reminders_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(String(255), default=None)
    execution_time = Column(DateTime)


