from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from repository.tourist_repository import TouristRepository
from services.clustering_service import DMeansClustering
from services.excursion import ExcursionGroup
from services.poi_builder import POIBuilder
from services.apriori import Apriori
from model.tourist import Tourist

router = APIRouter()

@router.get("/recommendations", response_model=dict)
def get_recommendations(db: Session = Depends(get_db)):
    """
    Endpoint para gerar recomendações personalizadas para turistas.
    """
    # Passo 1: Buscar turistas do banco de dados
    tourist_repo = TouristRepository(db)
    tourists = tourist_repo.get_all()

    # Converter turistas para objetos do modelo Tourist
    tourist_objects = []
    for tourist in tourists:
        # Extração das preferências diretamente do JSON
        preferences = {
            'Adrenaline': tourist.preferences.get('Adrenaline', 0),
            'Heritage': tourist.preferences.get('Heritage', 0),
            'Gastronomy': tourist.preferences.get('Gastronomy', 0),
            'Health': tourist.preferences.get('Health', 0),
            'Museums': tourist.preferences.get('Museums', 0),
            'NaturalPhenomena': tourist.preferences.get('NaturalPhenomena', 0),
            'Party': tourist.preferences.get('Party', 0),
            'Sports': tourist.preferences.get('Sports', 0),
            'SunWaterSand': tourist.preferences.get('SunWaterSand', 0),
            'ThemeParks': tourist.preferences.get('ThemeParks', 0),
            'WildNature': tourist.preferences.get('WildNature', 0),
        }

        tourist_obj = Tourist(
            id = tourist.id,
            O=tourist.O,
            C=tourist.C,
            E=tourist.E,
            A=tourist.A,
            N=tourist.N,
            preferences=preferences
        )
        tourist_objects.append(tourist_obj)

    # Passo 2: Agrupamento com Personalidade usando D-Means
    dmeans = DMeansClustering()
    for tourist in tourist_objects:
        dmeans.add_tourist(tourist)

    # Passo 3: Criar Subgrupos baseados em personalidades semelhantes
    excursion_group = ExcursionGroup(tourist_objects)
    excursion_group.form_subgroups()

    # Passo 4: Construir listas de POIs usando Apriori
    poi_builder = POIBuilder(min_support=0.3, min_confidence=0.5)
    recommendations = {}

    for i, subgroup in enumerate(excursion_group.subgroups):
        # Construir listas baseadas em preferências e regras Apriori
        poi_builder.build_poi_lists(subgroup)

        recommendations[f"Subgroup_{i+1}"] = {
            "POI_Inclusion": subgroup.poi_inclusion,
            "POI_Exclusion": subgroup.poi_exclusion,
            "Applied_Rules": [
                {
                    "Antecedent": list(rule[0]),
                    "Consequent": list(rule[1]),
                    "Support": round(rule[2], 2),
                    "Confidence": round(rule[3], 2),
                }
                for rule in poi_builder.apriori.rules
            ]
        }

    # Passo 5: Retornar listas de recomendações por subgrupo
    return {
        "message": "Recomendações geradas com sucesso",
        "recommendations": recommendations
    }