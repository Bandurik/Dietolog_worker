from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from pytz import timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True)
    subscribed = Column(Boolean, default=False)
    subscription_end = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    diet_goal = Column(String, nullable=True)
    eating_schedule = Column(String, nullable=True)  # Новый столбец для режима питания
    current_week = Column(Integer, nullable=True, default=1)  # Номер текущей недели
    last_menu_sent = Column(DateTime, nullable=True)  # Дата последней отправки меню
    timezone = Column(String)  # Новый столбец для хранения часового пояса

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    payment_id = Column(String, unique=True)
    chat_id = Column(String)
    status = Column(String, default='pending')

engine = create_engine('sqlite:///local_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def add_user(chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if not user:
        msk_timezone = timezone('Europe/Moscow')
        new_user = User(chat_id=chat_id) (timezone='Europe/Moscow')  # Временная зона МСК
        session.add(new_user)
        session.commit()

def get_user(chat_id):
    return session.query(User).filter_by(chat_id=chat_id).first()

def update_subscription(chat_id, end_date):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.subscribed = True
        user.subscription_end = end_date
        session.commit()

def update_user_info(chat_id, age, weight, height, diet_goal):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.age = age
        user.weight = weight
        user.height = height
        user.diet_goal = diet_goal
        session.commit()

def update_eating_schedule(chat_id, eating_schedule):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.eating_schedule = eating_schedule
        session.commit()

def update_current_week(chat_id, current_week):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.current_week = current_week
        session.commit()

def update_last_menu_sent(chat_id, last_menu_sent):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user.last_menu_sent = last_menu_sent
        session.commit()

def add_payment(payment_id, chat_id):
    new_payment = Payment(payment_id=payment_id, chat_id=chat_id)
    session.add(new_payment)
    session.commit()

def get_pending_payments():
    return session.query(Payment).filter_by(status='pending').all()

def update_payment_status(payment_id, status):
    payment = session.query(Payment).filter_by(payment_id=payment_id).first()
    if payment:
        payment.status = status
        session.commit()

def delete_user(chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        session.delete(user)
        session.commit()
