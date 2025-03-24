from services.apriori import Apriori
from collections import defaultdict


class POIBuilder:

    def __init__(self, min_support=0.3, min_confidence=0.6):
        self.apriori = Apriori(min_support, min_confidence)

    def build_poi_lists(self, subgroup):
        # Passo 1: Lista baseada em médias
        self._build_based_on_averages(subgroup)

        # Passo 2: Aprimorar com regras de associação
        self._enhance_with_apriori_rules(subgroup)

    def _build_based_on_averages(self, subgroup):
        preference_sums = defaultdict(float)
        preference_counts = defaultdict(int)

        for tourist in subgroup.tourists:
            for category, rating in tourist.preferences.items():
                if rating >= 3:  # Considera apenas ratings relevantes
                    preference_sums[category] += rating
                    preference_counts[category] += 1

        subgroup.poi_inclusion = [
            category for category in preference_sums
            if (preference_sums[category] / preference_counts[category]) >= 3
        ]
        subgroup.poi_exclusion = [
            category for category in preference_sums
            if (preference_sums[category] / preference_counts[category]) < 3
        ]

    def _enhance_with_apriori_rules(self, subgroup):
        # Gerar transações para Apriori
        transactions = [[
            category for category, rating in tourist.preferences.items()
            if rating >= 3
        ] for tourist in subgroup.tourists]

        # Extrair regras
        self.apriori.fit(transactions)

        # Aplicar regras para incluir POIs adicionais
        for antecedent, consequent, _, _ in self.apriori.rules:
            for poi in consequent:
                if poi not in subgroup.poi_inclusion and poi not in subgroup.poi_exclusion:
                    subgroup.poi_inclusion.append(poi)
