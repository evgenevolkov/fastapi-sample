from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text 
from sqlalchemy.sql.sqltypes import TIMESTAMP 

from .setup import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, server_default=text('False')) #soft delete
    created_at = Column(TIMESTAMP(timezone=True), nullable=False
                        , server_default=text('NOW()'))
    

class Texts(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id", onupdate='CASCADE', ondelete='CASCADE'), 
        nullable=False)
    name = Column(String, nullable=False, server_default='Unnamed')
    content = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, server_default=text('False')) #soft delete
    created_at = Column(TIMESTAMP(timezone=True), nullable=False
                        , server_default=text('NOW()'))
    
    owner = relationship("Users")