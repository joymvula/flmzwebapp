from datetime import datetime
from flask_login import UserMixin
from extensions import db

# ========== USER MODEL ==========
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

# ========== CHILD MODEL ==========
class Child(db.Model):
    __tablename__ = 'child'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))

    # Relationships
    visits = db.relationship('HomeVisit', back_populates='child', cascade="all, delete-orphan")
    vulnerabilities = db.relationship('Vulnerability', back_populates='child', cascade="all, delete-orphan")
    literacy_assessments = db.relationship('LiteracyAssessment', back_populates='child', cascade="all, delete-orphan")
    issues = db.relationship('Issue', back_populates='child', cascade="all, delete-orphan")

# ========== HOME VISIT MODEL ==========
class HomeVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    findings = db.Column(db.Text)

    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
    child = db.relationship('Child', back_populates='visits')

    issues = db.relationship('Issue', backref='visit', lazy='dynamic')

# ========== VULNERABILITY MODEL ==========
class Vulnerability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer)
    data = db.Column(db.JSON)

    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
    child = db.relationship('Child', back_populates='vulnerabilities')

# ========== LITERACY ASSESSMENT MODEL ==========
class LiteracyAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    ticks = db.Column(db.Integer)
    level = db.Column(db.String(20))

    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
    child = db.relationship('Child', back_populates='literacy_assessments')

# ========== ISSUE MODEL ==========
class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open')
    visit_id = db.Column(db.Integer, db.ForeignKey('home_visit.id'))  

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    child = db.relationship('Child', back_populates='issues')
