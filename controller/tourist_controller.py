# app/controller/tourist_controller.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import requests
from pydantic import BaseModel

from repository.tourist_repository import TouristRepository
from model.tourist import Tourist
from schemas.tourist_schema import TouristCreate, TouristUpdate
from db.database import get_db

router = APIRouter()


# ======== MODELO PARA FORMULÁRIO OCEAN =========
class FormOCEANRequest(BaseModel):
    silenceInConversations: int
    leadershipInGroups: int
    dailyEnergy: int
    empathy: int
    harshExpression: int
    optimismWithPeople: int
    difficultyWithOrganization: int
    easeToStartTasks: int
    reliability: int
    multitaskingConcern: int
    lackOfEnergy: int
    calmness: int
    interestInArts: int
    lowInterestInAbstractIdeas: int
    creativity: int


# ======== FUNÇÕES DE CÁLCULO =========
def calcular_ocean(form):
    E = ((6 - form.get('silenceInConversations', 0)) + form.get('leadershipInGroups', 0) + form.get('dailyEnergy', 0)) / 3
    A = (form.get('empathy', 0) + (6 - form.get('harshExpression', 0)) + form.get('optimismWithPeople', 0)) / 3
    C = ((6 - form.get('difficultyWithOrganization', 0)) + form.get('easeToStartTasks', 0) + form.get('reliability', 0)) / 3
    N = (form.get('multitaskingConcern', 0) + form.get('lackOfEnergy', 0) + (6 - form.get('calmness', 0))) / 3
    O = (form.get('interestInArts', 0) + (6 - form.get('lowInterestInAbstractIdeas', 0)) + form.get('creativity', 0)) / 3

    return {
        'O': round(O, 2),
        'C': round(C, 2),
        'E': round(E, 2),
        'A': round(A, 2),
        'N': round(N, 2)
    }

def calcular_preferences(ocean):
    O, C, E, A, N = ocean['O'], ocean['C'], ocean['E'], ocean['A'], ocean['N']
    preferences = {
        "F1": ((0.715 * E - 0.32 * C) + 0.32) / (0.715 + 0.32),
        "F2": ((0.404 * E + 0.573 * A - 0.223 * C) + 0.223) / (0.977 + 0.223),
        "F3": ((0.751 * E - 0.05 * A + 0.129 * N - 0.115 * O - 0.108 * C) + 0.273) / (0.88 + 0.273),
        "F4": ((0.617 * E + 0.076 * N - 0.232 * O) + 0.232) / (0.693 + 0.232),
        "F5": ((0.525 * A + 0.078 * N + 0.078 * O - 0.182 * C) + 0.182) / (0.681 + 0.182),
        "F6": ((0.79 * E - 0.123 * A + 0.128 * N - 0.204 * O - 0.077 * C) + 0.404) / (0.918 + 0.404),
        "F7": A,
        "F8": ((0.717 * E - 0.309 * A - 0.152 * O - 0.15 * C) + 0.611) / (0.717 + 0.611),
        "F9": ((0.459 * E + 0.187 * A - 0.116 * O - 0.089 * C) + 0.205) / (0.646 + 0.205),
        "F10": ((0.649 * E - 0.168 * A + 0.144 * N - 0.143 * O + 0.079 * C) + 0.311) / (0.872 + 0.311),
        "F11": ((0.336 * E + 0.605 * A - 0.365 * C) + 0.365) / (0.941 + 0.365),
    }
    return {k: round(v, 2) for k, v in preferences.items()}


# ======== ROTAS DE CRIAÇÃO DE TURISTA =========
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

@router.post("/tourists/from-profile/{profile_id}")
def create_tourist_from_profile(profile_id: str, db: Session = Depends(get_db)):
    java_api_url = f"http://localhost:8080/profile/{profile_id}"
    response = requests.get(java_api_url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Profile not found in Java API")

    profile_data = response.json()
    form_ocean = profile_data.get("preferences", {}).get("formOCEAN", {})

    if not form_ocean:
        raise HTTPException(status_code=400, detail="FormOCEAN data not found in profile")

    ocean_scores = calcular_ocean(form_ocean)
    calculated_preferences = calcular_preferences(ocean_scores)

    tourist = Tourist(
        id=profile_data["id"],
        O=ocean_scores["O"],
        C=ocean_scores["C"],
        E=ocean_scores["E"],
        A=ocean_scores["A"],
        N=ocean_scores["N"],
        preferences=calculated_preferences
    )

    repo = TouristRepository(db)
    created = repo.add(tourist)
    return created

@router.post("/tourists/from-form-ocean-json")
def create_tourist_from_json(profile_data: dict = Body(...), db: Session = Depends(get_db)):
    preferences = profile_data.get("preferences", {})
    form_ocean = preferences.get("formOCEAN", {})

    if not form_ocean:
        raise HTTPException(status_code=400, detail="FormOCEAN data not found in profile")

    ocean_scores = calcular_ocean(form_ocean)

    tourist = Tourist(
        id=profile_data.get("id", None),
        O=ocean_scores["O"],
        C=ocean_scores["C"],
        E=ocean_scores["E"],
        A=ocean_scores["A"],
        N=ocean_scores["N"],
        preferences=preferences
    )

    repo = TouristRepository(db)
    created = repo.add(tourist)
    return created


# ======== ROTAS DE RECOMENDAÇÃO =========
@router.post("/recommendations/from-form-ocean/{tourist_id}", response_model=dict)
def generate_recommendation_with_id(tourist_id: int, form: FormOCEANRequest, db: Session = Depends(get_db)):
    repo = TouristRepository(db)
    tourist = repo.get_by_id(tourist_id)

    if not tourist:
        raise HTTPException(status_code=404, detail="Turista não encontrado")

    ocean_scores = calcular_ocean(form.dict())
    preferences = calcular_preferences(ocean_scores)

    tourist.O = ocean_scores["O"]
    tourist.C = ocean_scores["C"]
    tourist.E = ocean_scores["E"]
    tourist.A = ocean_scores["A"]
    tourist.N = ocean_scores["N"]
    tourist.preferences = preferences
    repo.update(tourist)

    top_2 = sorted(preferences.items(), key=lambda x: x[1], reverse=True)[:2]
    top_2_labels = [label for label, _ in top_2]

    return {
        "tourist_id": tourist_id,
        "top_2_preferences": top_2_labels
    }


# ======== ROTAS DE LEITURA, ATUALIZAÇÃO E EXCLUSÃO =========
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
