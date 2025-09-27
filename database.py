from datetime import datetime
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.BigInteger, primary_key=True)
    username = sq.Column(sq.String(length=100))
    created_at = sq.Column(sq.DateTime, default=datetime.utcnow)

class Word(Base):
    __tablename__ = 'words'

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=100), nullable=False)
    translation = sq.Column(sq.String(length=100), nullable=False)
    is_common = sq.Column(sq.Boolean, default=True)

class UserWord(Base):
    __tablename__ = 'user_words'

    id = sq.Column(sq.Integer, primary_key=True)
    word_id = sq.Column(sq.Integer, sq.ForeignKey('words.id'), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.utcnow)

    word = relationship(Word, backref='user_words')
    user = relationship(User, backref='user_words')
