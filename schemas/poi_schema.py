from typing import Optional
from pydantic import BaseModel

class PoiBase(BaseModel):
    name: str
    address: Optional[str] = None
    transportation: Optional[str] = None  # "Locomoção" ou null
    list_type: str  # Ex: "Lista"
    category: str  # Ex: "Praia", "Patrimônio Cultural", etc.

class PoiCreate(PoiBase):
    pass

class PoiUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    transportation: Optional[str] = None
    list_type: Optional[str] = None
    category: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Biblioteca Pública Benedito Leite",
                "address": "Praça Deodoro, s/n - Centro, São Luís - MA, 65000-000",
                "transportation": "Locomoção",
                "list_type": "Lista",
                "category": "Patrimônio Cultural"
            }
        }

class PoiResponse(PoiBase):
    id: int

    class Config:
        orm_mode = True
