from sqlalchemy import Column, Integer, Float, String, ForeignKey
from db.database import Base

class Preferences(Base):
    __tablename__ = "preferences"
    __table_args__ = {'schema': 'persona_tour_recommendation'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    num = Column(String)
    score = Column(Float)
    tourist_id = Column(Integer, ForeignKey("persona_tour_recommendation.tourists.id"))  # Relaciona com a tabela tourists

    def __init__(self, name: str, num: str, score: float):
        self.name = name
        self.num = num.upper()  # Ex: 'F1'
        self.score = score

    def to_dict(self):
        return {
            "name": self.name,
            "num": self.num,
            "score": round(self.score, 2)
        }

    def __repr__(self):
        return f"Preference(name='{self.name}', num='{self.num}', score={self.score})"
