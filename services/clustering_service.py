import math


class Cluster:

    def __init__(self, centroid):
        self.centroid = centroid  # Tuple (O, C, E, A, N)
        self.tourists = []

    def add_tourist(self, tourist):
        self.tourists.append(tourist)
        tourist.cluster = self

    def update_centroid(self):
        if not self.tourists:
            return

        sum_O = sum(t.O for t in self.tourists)
        sum_C = sum(t.C for t in self.tourists)
        sum_E = sum(t.E for t in self.tourists)
        sum_A = sum(t.A for t in self.tourists)
        sum_N = sum(t.N for t in self.tourists)
        n = len(self.tourists)

        self.centroid = (sum_O / n, sum_C / n, sum_E / n, sum_A / n, sum_N / n)

    def __repr__(self):
        return f"Cluster(Centróide={self.centroid}, Turistas={len(self.tourists)})"


class DMeansClustering:

    def __init__(self, similarity_threshold=0.8):
        self.clusters = []
        self.similarity_threshold = similarity_threshold

    def add_tourist(self, new_tourist):
        if not self.clusters:
            self._create_new_cluster(new_tourist)
        else:
            best_cluster = self._find_best_cluster(new_tourist)
            if best_cluster:
                best_cluster.add_tourist(new_tourist)
                best_cluster.update_centroid()
            else:
                self._create_new_cluster(new_tourist)

        self._reassign_until_convergence()

    def _create_new_cluster(self, tourist):
        new_cluster = Cluster(
            (tourist.O, tourist.C, tourist.E, tourist.A, tourist.N))
        new_cluster.add_tourist(tourist)
        self.clusters.append(new_cluster)

    def _find_best_cluster(self, tourist):
        best_cluster = None
        max_similarity = 0

        for cluster in self.clusters:
            similarity = self._calculate_similarity(tourist, cluster.centroid)
            if similarity > max_similarity and similarity >= self.similarity_threshold:
                max_similarity = similarity
                best_cluster = cluster

        return best_cluster

    def _calculate_similarity(self, tourist, centroid):
        distance = math.sqrt((tourist.O - centroid[0])**2 +
                             (tourist.C - centroid[1])**2 +
                             (tourist.E - centroid[2])**2 +
                             (tourist.A - centroid[3])**2 +
                             (tourist.N - centroid[4])**2)
        max_distance = math.sqrt(5)  # 5 dimensões normalizadas [0-1]
        return 1 - (distance / max_distance)

    def _reassign_until_convergence(self, max_iterations=100, tolerance=1e-6):
        for _ in range(max_iterations):
            old_centroids = [cluster.centroid for cluster in self.clusters]

            # Reatribuir todos os turistas
            all_tourists = []
            for cluster in self.clusters:
                all_tourists.extend(cluster.tourists)
                cluster.tourists = []

            for tourist in all_tourists:
                best_cluster = self._find_best_cluster(tourist)
                if best_cluster:
                    best_cluster.add_tourist(tourist)
                else:
                    self._create_new_cluster(tourist)

            # Atualizar centróides
            for cluster in self.clusters:
                cluster.update_centroid()

            # Verificar convergência
            new_centroids = [cluster.centroid for cluster in self.clusters]
            if self._centroids_changed(old_centroids, new_centroids,
                                       tolerance):
                break

    def _centroids_changed(self, old, new, tolerance):
        if len(old) != len(new):
            return True
        return any(
            any(
                abs(o - n) > tolerance
                for o, n in zip(old_centroid, new_centroid))
            for old_centroid, new_centroid in zip(old, new))