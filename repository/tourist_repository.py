from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from model.tourist import  Tourist

class TouristRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, tourist: Tourist) -> None:
        self.session.add(tourist)
        self.session.commit()

    def get_by_id(self, tourist_id: int) -> Tourist:
        return self.session.query(Tourist).filter_by(id=tourist_id).first()

    def get_all(self):
        return self.session.query(Tourist).all()

    def update(self, tourist_id: int, **kwargs):
        tourist = self.get_by_id(tourist_id)
        if tourist:
            for key, value in kwargs.items():
                if hasattr(tourist, key):
                    setattr(tourist, key, value)
            self.session.commit()
            return tourist
        return None

    def delete(self, tourist_id: int) -> bool:
        tourist = self.get_by_id(tourist_id)
        if tourist:
            self.session.delete(tourist)
            self.session.commit()
            return True
        return False