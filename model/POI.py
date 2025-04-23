from sqlalchemy import Column, Integer, String
from db.database import Base

class POI(Base):
    __tablename__ = "POI"
    __table_args__ = {'schema': 'persona_tour_recommendation'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    address = Column(String, nullable=True)
    transportation = Column(String, nullable=True)
    list_type = Column(String)
    category = Column(String)
