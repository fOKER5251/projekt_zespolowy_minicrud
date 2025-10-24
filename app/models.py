from sqlalchemy import Column, Integer, String
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    group_code = Column(String(40), nullable=False)
