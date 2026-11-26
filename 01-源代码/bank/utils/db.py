import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, backref, joinedload
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, List, Any
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()  # 这行代码会读取 .env 文件中的变量

Base = declarative_base()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_CHARSET = os.getenv('DB_CHARSET')

database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(database_url,
                       pool_size=10,
                       max_overflow=20,
                       pool_recycle=3600,
                       pool_timeout=30,
                       pool_pre_ping=True,
                       )
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    money = Column(Integer, nullable=False)


class Merchant(Base):
    __tablename__ = 'merchant'

    id = Column(Integer, primary_key=True)
    merchant_id = Column(String(64),unique=True,nullable=False)
    merchant_name = Column(String(128),unique=True,nullable=False)
    public_key = Column(Text,nullable=False)
    callback_url = Column(String(512),nullable=False)
    return_url = Column(String(512),nullable=False)
    status = Column(String(20),nullable=False,default='active')
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow,nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), unique=True, nullable=False)
    order_id = Column(String(64), nullable=False)
    merchant_id = Column(String(64),ForeignKey('merchant.merchant_id'), nullable=False)
    amount = Column(Integer, nullable=False, comment='交易金额，单位：分')
    status = Column(String(20), nullable=False, comment='pending / paid / failed')
    sign = Column(Text, nullable=False, comment='电商原始签名（hex）')
    encrypted_result = Column(Text, nullable=True, comment='加密后的支付结果密文')
    callback_status = Column(String(20), nullable=False, default='pending')
    callback_attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at = Column(DateTime,default=datetime.utcnow,nullable=False)

    merchant = relationship("Merchant", backref="transactions")

Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

