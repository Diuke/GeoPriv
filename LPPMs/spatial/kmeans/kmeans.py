from builtins import range
import random

class Kmeans:
    """
    K-means algorithm implementation for GridPoints as a clustering algorithm
    """
    def __init__(self, point_list, mink, seed):
        """Constructor
        :param mink: minimum points to be considered cluster globaly from Spatial
        :type mink: number
        :param point_list: List of points to be processed
        :type point_list: List 
        :param seed: Random seed for reproducibility
        :type seed: number
        """
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
        for p in point_list: #Remove points that already have K points clustered from gridification
            if p.grouped >= mink:
                c = Cluster(p.lat, p.lon)
                c.cont = p.grouped
                self.ready_points.append(c)
            else:
                self.point_list.append(p)
                self.min_lat = min(self.min_lat, p.lat)
                self.max_lat = max(self.max_lat, p.lat)
                self.min_lon = min(self.min_lon, p.lon)
                self.max_lon = max(self.max_lon, p.lon)

    def error(self):
        """Calculates quadratic error"""
        e = 0
        for c in self.cluster_list:
            e += c.error()
        return e

    def clean_clusters(self):
        """Removes all points from all clusters"""
        for c in self.cluster_list:
            c.points = []

    
    def assign_clusters(self):
        """Assigns each point to the closest cluster using the calc_distance() method.
        Uses euclidean distance
        """
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

    
    def calculate_clusters(self, n):
        """Selects random points and iterates to find the clusters
        :param: n: Number of clusters specified
        :type: n: number
        """
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
        while not self.all_locked(self.cluster_list) and iterations < 1000: #Allows 1000 iterations
            iterations += 1
            for c in self.cluster_list:
                c.adjust_centroid()
            self.assign_clusters()
        #self.print_clusters()
        for c in self.ready_points:
            self.cluster_list.append(c)
            

    def all_locked(self, cluster_list):
        """Checks if every centroid is locked. Locked means its centroid didn't changed in the last iteration."""
        for c in cluster_list:
            if not c.lock:
                return False
        return True

class Cluster:
    """Cluster model"""
    def __init__(self, lat, lon):
        """Constructor
        :param: lat: Latitude
        :type lat: float
        :param: lon: Longitude
        :type lon: float
        """
        self.cont = 0
        self.points = []
        self.lat = lat
        self.lon = lon
        self.lock = False

    def error(self):
        """Quadratic error of the cluster points"""
        e = 0
        for p in self.points:
            e += p.calc_distance(self.lat, self.lon)**2
        return e

    def add_point(self, point):
        """Add point to cluster"""
        self.points.append(point)

    def adjust_centroid(self):
        """Adjusts the centroid of the cluster by calculating the mean of latitudes and longitues 
        of all points in the cluster
        """
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
        
        if abs(prev_lat - prom_lat) < 0.0001 or abs(prev_lon - prom_lon) < 0.0001:
            self.lock = True
        else:
            self.lat = prom_lat
            self.lon = prom_lon
