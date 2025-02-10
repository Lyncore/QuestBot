from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Session
import os

class Base(DeclarativeBase): pass

class OTPKey(Base):
    __tablename__ = 'otp_keys'
    id = Column(Integer, primary_key=True)
    secret = Column(String(40), nullable=False)

class Admin(Base):
    __tablename__ = 'admins'
    user_id = Column(BigInteger, primary_key=True)

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    team_name = Column(String(50), nullable=False)
    description = Column(Text)
    leader_id = Column(BigInteger)
    code_word = Column(String(50), nullable=False)
    welcome_message = Column(Text)
    final_message = Column(Text)
    current_chain_order = Column(Integer, default=0)
    chains = relationship("Chain", back_populates="team")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    task_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    photo = Column(String(255))
    sticker = Column(String(255))
    animation = Column(String(255))
    location = Column(String(255), nullable=False)
    code_word = Column(String(50), nullable=False)
    chains = relationship("Chain", back_populates="task")

class Chain(Base):
    __tablename__ = 'chains'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    order = Column(Integer, nullable=False)
    team = relationship("Team", back_populates="chains")
    task = relationship("Task", back_populates="chains")

# Инициализация БД
def init_session():
    DATABASE_URL = os.getenv('DATABASE_URL')
    print(DATABASE_URL)
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session()