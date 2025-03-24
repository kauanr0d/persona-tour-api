# app/models/tourist.py
from sqlalchemy import Column, Integer, Float, String
from db.database import Base
from sqlalchemy.dialects.postgresql import JSON


class Tourist(Base):
    __tablename__ = "tourists"
    __table_args__ = {'schema': 'persona_tour_recommendation'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # autoincrement adicionado
    O = Column(Float)
    C = Column(Float)
    E = Column(Float)
    A = Column(Float)
    N = Column(Float)
    preferences = Column(JSON, nullable=True)  # Aqui usamos o tipo JSON
