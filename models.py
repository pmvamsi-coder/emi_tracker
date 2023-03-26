from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Emi(db.Model):
    loan_name = db.Column(db.Text, primary_key=True, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    emi_amount = db.Column(db.Float, nullable=False)
    paid_off = db.Column(db.Boolean, nullable=False, default=False)
    created_date = db.Column(db.Date, default=datetime.utcnow)


class EmiSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_name = db.Column(db.String(50), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    opening_balance = db.Column(db.Numeric(10, 2), nullable=False)
    emi = db.Column(db.Numeric(10, 2), nullable=False)
    principal = db.Column(db.Numeric(10, 2), nullable=False)
    interest = db.Column(db.Numeric(10, 2), nullable=False)
    closing_balance = db.Column(db.Numeric(10, 2), nullable=False)
    emi_date = db.Column(db.Date, nullable=False)
    date_created = db.Column(db.Date, default=datetime.utcnow)

    def __repr__(self):
        return f'<EmiSchedule {self.id}>'
