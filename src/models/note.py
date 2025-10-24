from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from src.models.user import db


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # store tags as JSON when supported (Postgres JSON/JSONB, SQLite will store as TEXT)
    # Use SQLAlchemy's JSON type so it maps appropriately across DB backends.
    tags = db.Column(db.JSON, nullable=True, default=list)
    # event date and time (stored as strings for simplicity)
    event_date = db.Column(db.String(10), nullable=True)  # YYYY-MM-DD
    event_time = db.Column(db.String(8), nullable=True)   # HH:MM:SS
    # position for manual ordering (lower = earlier in list)
    position = db.Column(db.Integer, nullable=True, default=0)
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # tags is stored as JSON where supported; normalize to list
            'tags': self.tags if self.tags else [],
            'event_date': self.event_date,
            'event_time': self.event_time,
            'position': self.position
        }

