from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from repository.tourist_repository import TouristRepository
from services.clustering_service import DMeansClustering
from services.excursion import ExcursionGroup
from services.poi_builder import POIBuilder
from services.apriori import AprioriPOI, Apriori
from model.tourist import Tourist
import numpy as np
from sklearn.preprocessing import StandardScaler
from model.tourist import Tourist  # Verifique se está no lugar certo
import pandas as pd

router = APIRouter()

@router.get("/recommendations", response_model=dict)
def get_recommendations(db: Session = Depends(get_db)):
    """
    Endpoint para gerar recomendações personalizadas para turistas.
    """
    # Mapeamento dos códigos para nomes das categorias em português
    CATEGORY_MAP = {
        "F1": "Adrenalina",
        "F2": "Natureza Selvagem",
        "F3": "Festas e Vida Noturna",
        "F4": "Sol e Praia",
        "F5": "Museus e Cultura",
        "F6": "Parques Temáticos",
        "F7": "Patrimônio Cultural",
        "F8": "Esportes",
        "F9": "Gastronomia",
        "F10": "Bem-estar e Saúde",
        "F11": "Paisagens Naturais"
    }

    # Passo 1: Buscar turistas do banco de dados
    tourist_repo = TouristRepository(db)
    tourists = tourist_repo.get_all()

    # Passo 2: Padronizar dados de personalidade com StandardScaler
    personality_data = np.array([[t.O, t.C, t.E, t.A, t.N] for t in tourists])
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(personality_data)

    # Passo 3: Criar objetos Tourist com dados normalizados
    tourist_objects = []
    for i, tourist in enumerate(tourists):
        preferences = tourist.preferences
        tourist_obj = Tourist(
            id=tourist.id,
            O=scaled_data[i][0],
            C=scaled_data[i][1],
            E=scaled_data[i][2],
            A=scaled_data[i][3],
            N=scaled_data[i][4],
            preferences=preferences
        )
        tourist_objects.append(tourist_obj)

    # Passo 4: Agrupamento com Personalidade usando D-Means
    dmeans = DMeansClustering()
    for tourist in tourist_objects:
        dmeans.add_tourist(tourist)

    # Passo 5: Criar Subgrupos baseados em personalidades semelhantes
    excursion_group = ExcursionGroup(tourist_objects)
    excursion_group.form_subgroups()

    # Passo 6: Construir listas de POIs usando Apriori
    poi_builder = POIBuilder(min_support=0.3, min_confidence=0.5)
    recommendations = {}

    for i, subgroup in enumerate(excursion_group.subgroups):
        poi_builder.build_poi_lists(subgroup)

        # Traduz POIs nas listas e regras
        translated_inclusion = [CATEGORY_MAP.get(poi, poi) for poi in subgroup.poi_inclusion]
        translated_exclusion = [CATEGORY_MAP.get(poi, poi) for poi in subgroup.poi_exclusion]
        translated_rules = [
            {
                "Antecedent": [CATEGORY_MAP.get(poi, poi) for poi in rule[0]],
                "Consequent": [CATEGORY_MAP.get(poi, poi) for poi in rule[1]],
                "Support": round(rule[2], 2),
                "Confidence": round(rule[3], 2),
            }
            for rule in poi_builder.apriori.rules
        ]

        recommendations[f"Subgrupo_{i+1}"] = {
            "POIs a Incluir": translated_inclusion,
            "POIs a Excluir": translated_exclusion,
            "Regras Aplicadas": translated_rules
        }

    # Passo 7: Retornar listas de recomendações por subgrupo
    return {
        "mensagem": "Recomendações geradas com sucesso",
        "recomendacoes": recommendations
    }



@router.get("/recommendations/subgroups", response_model=dict)
def generate_recommendations_with_subgroups(db: Session = Depends(get_db)):
    """
    Gera recomendações de POIs para subgrupos formados com base nos clusters e perfis de personalidade dos turistas.
    """
    # 1. Obter todos os turistas
    repo = TouristRepository(db)
    tourists = repo.get_all()

    # 2. Criar ExcursionGroup e formar subgrupos com base nos clusters
    excursion_group = ExcursionGroup(tourists)
    excursion_group.form_subgroups()

    # 3. Aplicar Apriori nos subgrupos gerados
    apriori_poi = AprioriPOI(subgroups=excursion_group.subgroups, min_support=0.3, min_confidence=0.6)
    apriori_poi.process_subgroups()

    # 4. Criar resposta JSON com os subgrupos, POIs e regras aplicadas
    response = {}
    for idx, subgroup in enumerate(excursion_group.subgroups):
        response[f"Subgroup_{idx + 1}"] = {
            "POI_Inclusion": subgroup.poi_inclusion,
            "POI_Exclusion": subgroup.poi_exclusion,
            "Applied_Rules": [
                {
                    "Rule": f"{set(antecedent)} => {set(consequent)}",
                    "Support": support,
                    "Confidence": confidence
                }
                for antecedent, consequent, support, confidence in subgroup.get_poi_rules()
            ]
        }

    return {
        "message": "Recomendações geradas com sucesso para subgrupos",
        "recommendations": response
    }

@router.get("/recommendations/preferences", response_model=dict)
def generate_recommendations_by_preferences(db: Session = Depends(get_db)):
    """
    Gera recomendações de POIs baseadas nas preferências gerais dos turistas usando o algoritmo Apriori.
    """
    # 1. Obter todos os turistas do banco de dados
    repo = TouristRepository(db)
    tourists = repo.get_all()

    # 2. Criar transações baseadas nas preferências dos turistas
    transactions = [
        [poi_category for poi_category, rating in tourist.preferences.items() if rating >= 3]
        for tourist in tourists
    ]

    # 3. Aplicar o Apriori para encontrar padrões de associação
    apriori = Apriori(min_support=0.3, min_confidence=0.6)
    apriori.fit(transactions)

    # 4. Montar a resposta com regras aplicadas e POIs recomendados
    response = {
        "POI_Inclusion": list({poi for _, consequent, _, _ in apriori.rules for poi in consequent}),
        "Applied_Rules": [
            {
                "Antecedent": list(antecedent),
                "Consequent": list(consequent),
                "Support": support,
                "Confidence": confidence
            }
            for antecedent, consequent, support, confidence in apriori.rules
        ]
    }

    return {
        "message": "Recomendações geradas com sucesso com base nas preferências gerais dos turistas",
        "recommendations": response
    }


@router.get("/recommendations/{tourist_id}", response_model=dict)
def generate_individual_recommendation(tourist_id: int, db: Session = Depends(get_db)):
    """
    Gera uma recomendação de POIs personalizada para um turista específico com base no seu perfil.
    Retorna apenas a lista de POI_Inclusion.
    """
    repo = TouristRepository(db)
    tourist = repo.get_by_id(tourist_id)

    if not tourist:
        return {"message": "Turista não encontrado", "POI_Inclusion": []}

    # Criar transações com base nas preferências do turista
    preferred_categories = [poi for poi, rating in tourist.preferences.items() if rating >= 3]

    # Aplicar Apriori
    apriori = Apriori(min_support=0.5, min_confidence=0.7)
    apriori.fit([preferred_categories])

    # Construir lista de POI_Inclusion com consequentes das regras geradas
    poi_inclusion = list({poi for _, consequent, _, _ in apriori.rules for poi in consequent})

    return {
        "POI_Inclusion": poi_inclusion
    }
