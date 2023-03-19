from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Emi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_name = db.Column(db.Text, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    emi_amount = db.Column(db.Float, nullable=False)
    paid_off = db.Column(db.Boolean, nullable=False, default=False)
