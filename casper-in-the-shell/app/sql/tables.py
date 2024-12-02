from sqlalchemy import (DECIMAL, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(31), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

class Command(Base):
    __tablename__ = 'commands'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    command = Column(String(511), nullable=False)

class Macro(Base):
    __tablename__ = 'macros'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)

class MacroCommand(Base):
    __tablename__ = 'macro_commands'

    macro_id = Column(Integer, primary_key=True)
    command_id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)