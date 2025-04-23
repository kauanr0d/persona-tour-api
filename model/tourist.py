from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship
from db.database import Base
from .preferences import Preferences  # Corrigido para referência relativa

class Tourist(Base):
    __tablename__ = "tourists"
    __table_args__ = {'schema': 'persona_tour_recommendation'}

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    O = Column(Float)
    C = Column(Float)
    E = Column(Float)
    A = Column(Float)
    N = Column(Float)

    # Relacionamento de 1 para N com Preferences
    preferences = relationship("Preferences", backref="tourist", cascade="all, delete-orphan")

    def get_top_preference(self):
        """
        Retorna o fator de preferência com maior valor.
        Exemplo de retorno: ('F3', 1.78)
        """
        if not self.preferences:
            return None
        # Pega a preferência com maior pontuação
        top_preference = max(self.preferences, key=lambda p: p.score)
        return (top_preference.num, top_preference.score)  # Retorna como tupla (num, score)
