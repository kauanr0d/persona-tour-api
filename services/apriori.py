from itertools import combinations
from collections import defaultdict


class Apriori:
    def __init__(self, min_support=0.3, min_confidence=0.6):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.itemsets = []
        self.rules = []

    def fit(self, transactions):
        self.transactions = transactions
        self.items = self._get_unique_items()
        self.itemsets = self._find_frequent_itemsets()
        self.rules = self._generate_association_rules()

    def _get_unique_items(self):
        return list({item for transaction in self.transactions for item in transaction})

    def _find_frequent_itemsets(self):
        itemsets = []
        k = 1
        current_itemsets = [frozenset([item]) for item in self.items]

        while current_itemsets:
            counts = defaultdict(int)
            for transaction in self.transactions:
                for itemset in current_itemsets:
                    if itemset.issubset(transaction):
                        counts[itemset] += 1

            frequent = [
                itemset for itemset, count in counts.items()
                if count / len(self.transactions) >= self.min_support
            ]

            if not frequent:
                break

            itemsets.extend(frequent)
            current_itemsets = self._generate_candidates(frequent, k)
            k += 1

        return itemsets

    def _generate_candidates(self, itemsets, k):
        candidates = set()
        for i in range(len(itemsets)):
            for j in range(i + 1, len(itemsets)):
                union = itemsets[i].union(itemsets[j])
                if len(union) == k + 1:
                    candidates.add(union)
        return list(candidates)

    def _generate_association_rules(self):
        rules = []
        for itemset in self.itemsets:
            if len(itemset) < 2:
                continue

            for antecedent in combinations(itemset, len(itemset) - 1):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent

                antecedent_support = self._calculate_support(antecedent)
                if antecedent_support == 0:
                    continue

                rule_support = self._calculate_support(itemset)
                confidence = rule_support / antecedent_support

                if confidence >= self.min_confidence:
                    rules.append((
                        antecedent,
                        consequent,
                        rule_support,
                        confidence
                    ))

        return rules

    def _calculate_support(self, itemset):
        count = 0
        for transaction in self.transactions:
            if itemset.issubset(transaction):
                count += 1
        return count / len(self.transactions)


class AprioriPOI:
    def __init__(self, subgroups, min_support=0.3, min_confidence=0.6):
        self.subgroups = subgroups
        self.apriori = Apriori(min_support, min_confidence)

    def process_subgroups(self):
        for subgroup in self.subgroups:
            transactions = self._create_transactions(subgroup)
            self.apriori.fit(transactions)
            self._apply_rules_to_subgroup(subgroup)

    def _create_transactions(self, subgroup):
        return [
            [poi_category for poi_category, rating in tourist.preferences.items() if rating >= 3]
            for tourist in subgroup.tourists
        ]

    def _apply_rules_to_subgroup(self, subgroup):
        for antecedent, consequent, _, _ in self.apriori.rules:
            for poi in consequent:
                if poi not in subgroup.poi_inclusion:
                    subgroup.poi_inclusion.append(poi)

    def get_rules_report(self):
        report = []
        for subgroup in self.subgroups:
            subgroup_report = {
                "subgroup_id": id(subgroup),
                "num_rules": len(self.apriori.rules),
                "rules": [
                    f"{set(antecedent)} => {set(consequent)}"
                    for antecedent, consequent, _, _ in self.apriori.rules
                ]
            }
            report.append(subgroup_report)
        return report