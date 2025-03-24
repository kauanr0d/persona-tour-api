# app/controller/tourist_controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from repository.tourist_repository import TouristRepository
from model.tourist import Tourist
from schemas.tourist_schema import TouristCreate, TouristUpdate
from db.database import get_db

router = APIRouter()

@router.post("/tourists")
def create_tourist(tourist: TouristCreate, db: Session = Depends(get_db)):
    repo = TouristRepository(db)
    new_tourist = Tourist(**tourist.model_dump())
    return repo.add(new_tourist)

@router.post("/tourists/createTourists")
def create_tourists(tourists: List[TouristCreate], db: Session = Depends(get_db)):

    repo = TouristRepository(db)
    new_tourists = [Tourist(**tourist.model_dump()) for tourist in tourists]
    return repo.add_all(new_tourists)

@router.get("/tourists/{tourist_id}")
def get_tourist(tourist_id: int, db: Session = Depends(get_db)):
    repo = TouristRepository(db)
    tourist = repo.get_by_id(tourist_id)
    if not tourist:
        raise HTTPException(status_code=404, detail="Tourist not found")
    return tourist

@router.get("/tourists")
def list_tourists(db: Session = Depends(get_db)):
    repo = TouristRepository(db)
    return repo.get_all()

@router.put("/tourists/{tourist_id}")
def update_tourist(tourist_id: int, tourist: TouristUpdate, db: Session = Depends(get_db)):
    repo = TouristRepository(db)
    return repo.update(tourist_id, **tourist.dict(exclude_unset=True))

@router.delete("/tourists/{tourist_id}")
def delete_tourist(tourist_id: int, db: Session = Depends(get_db)):
    repo = TouristRepository(db)
    if not repo.delete(tourist_id):
        raise HTTPException(status_code=404, detail="Tourist not found")
    return {"message": "Tourist deleted successfully"}

