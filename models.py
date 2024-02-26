from sqlalchemy import Column, Integer, String
from database import Base


class DBItem(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
