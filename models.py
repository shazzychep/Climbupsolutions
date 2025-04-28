from flask_sqlalchemy import SQLAlchemy
from flask_mongoengine import MongoEngine
from datetime import datetime
import uuid

db = SQLAlchemy()
mongo = MongoEngine()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'consultant', 'client'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Consultant(db.Model):
    __tablename__ = 'consultants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    is_preferred = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('consultant', uselist=False))

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consultant_id = db.Column(db.String(36), db.ForeignKey('consultants.id'), nullable=False)
    client_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'scheduled', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    consultant = db.relationship('Consultant', backref=db.backref('appointments'))
    client = db.relationship('User', backref=db.backref('appointments'))

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    appointment_id = db.Column(db.String(36), db.ForeignKey('appointments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'pending', 'verified', 'failed'
    payment_proof_url = db.Column(db.String(255))
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    appointment = db.relationship('Appointment', backref=db.backref('payment', uselist=False))
    verifier = db.relationship('User', backref=db.backref('verified_payments'))

# MongoDB Models for Dynamic Rules
class PeakHourRule(mongo.Document):
    day = mongo.StringField(required=True)
    start_time = mongo.StringField(required=True)  # Format: "HH:MM"
    end_time = mongo.StringField(required=True)    # Format: "HH:MM"
    multiplier = mongo.FloatField(default=1.5)
    is_active = mongo.BooleanField(default=True)
    created_at = mongo.DateTimeField(default=datetime.utcnow)
    updated_at = mongo.DateTimeField(default=datetime.utcnow)

class SlotHoldRule(mongo.Document):
    hold_duration = mongo.IntField(required=True)  # Duration in seconds
    is_active = mongo.BooleanField(default=True)
    created_at = mongo.DateTimeField(default=datetime.utcnow)
    updated_at = mongo.DateTimeField(default=datetime.utcnow)

class ConsultantPreferenceRule(mongo.Document):
    preference_type = mongo.StringField(required=True)  # e.g., 'specialization', 'rating'
    value = mongo.StringField(required=True)
    weight = mongo.FloatField(default=1.0)
    is_active = mongo.BooleanField(default=True)
    created_at = mongo.DateTimeField(default=datetime.utcnow)
    updated_at = mongo.DateTimeField(default=datetime.utcnow) 