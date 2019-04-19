from builtins import range
import random

"""
K-means algorithm implementation for GridPoints
"""
class Kmeans:
    def __init__(self, point_list, mink, seed):
        self.locked = 0
        self.seed = seed
        self.cluster_list = []
        self.ready_points = []
        self.point_list = []
        self.mink = mink
        self.min_lat = 99999
        self.max_lat = -99999
        self.min_lon = 99999
        self.max_lon = -99999
        self.cluster_list = []
        #print(point_list)
        for p in point_list:
            if p.grouped >= mink:
                c = Cluster(p.lat, p.lon)
                c.cont = p.grouped
                self.ready_points.append(c)
                #print(str(c.lat) + "," + str(c.lon) + "," + str(c.cont))
            else:
                self.point_list.append(p)
                self.min_lat = min(self.min_lat, p.lat)
                self.max_lat = max(self.max_lat, p.lat)
                self.min_lon = min(self.min_lon, p.lon)
                self.max_lon = max(self.max_lon, p.lon)
                #print(str(p.lat) + "," + str(p.lon) + ",1")
        #self.print_clusters()
        #print("done")

    def error(self):
        e = 0
        for c in self.cluster_list:
            e += c.error()
        return e

    def clean_clusters(self):
        for c in self.cluster_list:
            c.points = []

    """
    Assigns each point to the closest cluster using the calc_distance() method.
    """
    def assign_clusters(self):
        self.clean_clusters()
        for point in self.point_list:
            min_dist = float('inf')
            min_cluster = None
            for cluster in self.cluster_list:
                distance = point.calc_distance(cluster.lat, cluster.lon)
                if distance < min_dist:
                    min_dist = distance
                    min_cluster = cluster
            min_cluster.add_point(point)

    """
    Selects random points and iterates to find the clusters
    """
    def calculate_clusters(self, n):
        iterations = 0
        taken = set()
        random.seed(self.seed)
        for i in range(n):
            pos = random.randrange(0, len(self.point_list), 1)
            while taken.__contains__(pos):
                pos = random.randrange(0, len(self.point_list), 1)
            taken.add(pos)
            lat = self.point_list[pos].lat
            lon = self.point_list[pos].lon
            self.cluster_list.append(Cluster(lat, lon))
        self.assign_clusters()
        while not self.all_locked(self.cluster_list) and iterations < 1000:
            iterations += 1
            for c in self.cluster_list:
                c.adjust_centroid()
            self.assign_clusters()
        #self.print_clusters()
        for c in self.ready_points:
            self.cluster_list.append(c)
            

    """
    Checks if every centroid is locked. Locked means its centroid didn't changed in the last iteration.
    """
    def all_locked(self, cluster_list):
        for c in cluster_list:
            if not c.lock:
                return False
        return True

class Cluster:
    def __init__(self, lat, lon):
        self.cont = 0
        self.points = []
        self.lat = lat
        self.lon = lon
        self.lock = False

    def error(self):
        e = 0
        for p in self.points:
            e += p.calc_distance(self.lat, self.lon)**2
        return e

    def add_point(self, point):
        self.points.append(point)

    def adjust_centroid(self):
        cont = 0
        if self.lock:
            return
        prom_lat = 0
        prom_lon = 0
        prev_lat = self.lat
        prev_lon = self.lon
        for point in self.points:
            prom_lat += point.lat*point.grouped
            prom_lon += point.lon*point.grouped
            cont += point.grouped
        self.cont = cont
        if cont != 0:
            prom_lat /= cont
            prom_lon /= cont
        else:
            prom_lat = self.lat
            prom_lon = self.lon
        #print(str(prev_lat) + " " + str(prom_lat))
        if abs(prev_lat - prom_lat) < 0.0001 or abs(prev_lon - prom_lon) < 0.0001:
            self.lock = True
            #Kmeans.locked += 1
            #print("Lock!" + str(Kmeans.locked))
        else:
            self.lat = prom_lat
            self.lon = prom_lon
