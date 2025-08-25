from datetime import datetime, UTC
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_suspended = db.Column(db.Boolean, default=False)
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')
    investments = db.relationship('Investment', backref='investor', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(64), index=True) # e.g., 'checking', 'savings', 'investment'
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')

    def __repr__(self):
        return f'<Account {self.id} ({self.account_type})>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(UTC))
    type = db.Column(db.String(64)) # e.g., 'deposit', 'withdrawal', 'transfer'
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    def __repr__(self):
        return f'<Transaction {self.id} ({self.type}) of {self.amount}>'

class InvestmentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    description = db.Column(db.Text)
    roi = db.Column(db.Float) # Return on Investment as a percentage
    duration = db.Column(db.Integer) # Duration in days
    investments = db.relationship('Investment', backref='plan', lazy='dynamic')

    def __repr__(self):
        return f'<InvestmentPlan {self.name}>'

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    start_date = db.Column(db.DateTime, index=True, default=lambda: datetime.now(UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('investment_plan.id'))

    def __repr__(self):
        return f'<Investment {self.id} by User {self.user_id} in Plan {self.plan_id}>'
