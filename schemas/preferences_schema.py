# app/schemas/preference.py
from pydantic import BaseModel


class PreferenceSchema(BaseModel):
    name: str
    num: str
    score: float

    class Config:
        schema_extra = {
            "example": {
                "name": "adrenaline",
                "num": "F1",
                "score": 0.65
            }
        }
