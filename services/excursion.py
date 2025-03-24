from collections import defaultdict
import math


class ExcursionGroup:

    def __init__(self, tourists):
        self.tourists = tourists
        self.subgroups = []

    def form_subgroups(self):
        if len(self.tourists) < 6:
            self.subgroups = [Subgroup(self.tourists)]
            return

        # Contar turistas por cluster
        cluster_counts = defaultdict(int)
        for tourist in self.tourists:
            if tourist.cluster:
                cluster_counts[tourist.cluster] += 1

        # Identificar clusters válidos (≥3 turistas)
        valid_clusters = [
            cluster for cluster, count in cluster_counts.items() if count >= 3
        ]

        if len(valid_clusters) >= 2:
            # Criar subgrupos principais
            for cluster in valid_clusters:
                subgroup_tourists = [
                    t for t in self.tourists if t.cluster == cluster
                ]
                self.subgroups.append(Subgroup(subgroup_tourists))

            # Redistribuir turistas restantes
            remaining_tourists = [
                t for t in self.tourists if cluster_counts[t.cluster] < 3
            ]
            for tourist in remaining_tourists:
                best_subgroup = self._find_best_subgroup(tourist)
                if best_subgroup:
                    best_subgroup.tourists.append(tourist)

            # Remover subgrupos vazios
            self.subgroups = [sg for sg in self.subgroups if sg.tourists]
        else:
            self.subgroups = [Subgroup(self.tourists)]

    def _find_best_subgroup(self, tourist):
        best_subgroup = None
        max_similarity = -1

        for subgroup in self.subgroups:
            if not subgroup.tourists:
                continue
            # Usar centróide do cluster original
            centroid = subgroup.tourists[0].cluster.centroid
            similarity = self._calculate_similarity(tourist, centroid)
            if similarity > max_similarity:
                max_similarity = similarity
                best_subgroup = subgroup

        return best_subgroup

    def _calculate_similarity(self, tourist, centroid):
        distance = math.sqrt((tourist.O - centroid[0])**2 +
                             (tourist.C - centroid[1])**2 +
                             (tourist.E - centroid[2])**2 +
                             (tourist.A - centroid[3])**2 +
                             (tourist.N - centroid[4])**2)
        max_distance = math.sqrt(5)
        return 1 - (distance / max_distance)


class Subgroup:

    def __init__(self, tourists):
        self.tourists = tourists
        self.poi_inclusion = []
        self.poi_exclusion = []
        self._poi_rules = []  # Novo atributo para armazenar regras

    def add_poi_rule(self, rule):
        self._poi_rules.append(rule)

    def get_poi_rules(self):
        return self._poi_rules
