from sqlalchemy import Column, Integer, String

from database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    text = Column(String)

    sender = Column(String)

    receiver = Column(String)

    status = Column(String, default="sent")

    whatsapp_id = Column(String)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # admin / user    