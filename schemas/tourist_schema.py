from typing import Optional, Dict
from pydantic import BaseModel


class TouristBase(BaseModel):
    O: float
    C: float
    E: float
    A: float
    N: float
    preferences: Dict[str, float]  # Um dicionário dinâmico, sem valores fixos


class TouristCreate(TouristBase):
    pass


class TouristUpdate(BaseModel):
    O: Optional[float] = None  # Pode ser ignorado
    preferences: Optional[Dict[str, float]] = None  # Pode ser ignorado ou atualizado parcialmente

    class Config:
        schema_extra = {
            "example": {
                "O": 0.75,
                "preferences": {
                    "F1": 4.0,
                    "F5": 3.8,
                    "F9": 2.7,
                }
            }
        }


class TouristResponse(TouristBase):
    id: int  # Para incluir o `id` no retorno

    class Config:
        orm_mode = True
