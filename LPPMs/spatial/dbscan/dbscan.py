import csv
class DBScan:
    """DBSCAN clustering algorithm"""
    point_list = [] #list of points
    cluster_list = [] #list of clusters
    ready_points = [] #list of points ready from gridification

    def __init__(self, point_list, mink):
        """Constructor
        :param point_list: List of points to be processed
        :type point_list: List
        :param mink: minimum number of points to be considered cluster (global Spatial parameter)
        :type mink: number
        """
        self.point_list = []
        self.cluster_list = []
        # Preprocess points to remove already complete clusters from gridification 
        for p in point_list:
            if p.grouped >= mink: 
                c = Cluster()
                c.add_point(p)
                self.ready_points.append(c)
            else:
                self.point_list.append(p)

    def fit(self, eps, min_size):
        """Calculate the clusters according to DBSCAN algorithm and the parameters specified
        :param eps: distance between points to be considered from the same cluster
        :type eps: float
        :param min_size: Minimum amount of points that a cluster need to have to be considered cluster.
        :type min_size: number
        """
        taken = set() #empty set of taken points
        cont = 0
        for point in self.point_list:
            if not taken.__contains__(point): #takes only non-taken points
                taken.add(point)
                cont += point.grouped
                c = Cluster()
                c.add_point(point)
                for test in c.points:
                    for p2 in self.point_list:
                        if not taken.__contains__(p2):
                            dist = test.calc_distance(p2.lat, p2.lon) 
                            if dist <= eps: 
                                taken.add(p2)
                                cont += p2.grouped
                                c.add_point(p2)
                if cont >= min_size:
                    self.cluster_list.append(c)
                cont = 0
        for ready in self.ready_points:
            self.cluster_list.append(ready)
        self.calculate_centroid()

    def calculate_centroid(self):
        """Calculate the centroid of the cluster as the mean of the latitudes and longitudes of its points"""
        total = 0
        for c in self.cluster_list:
            lat = 0
            lon = 0
            for p in c.points:
                total = total+p.grouped
                lat = lat+p.lat*p.grouped
                lon = lon+p.lon*p.grouped
            c.lat = lat/c.cont
            c.lon = lon/c.cont
        #print(total)

class Cluster:
    """Model of a cluster"""
    def __init__(self):
        """Constructor"""
        self.lat = 0
        self.lon = 0
        self.cont = 0
        self.points = []

    def add_point(self, point):
        """Add a point to the cluster.
        This updates the cont of the points of the cluster.
        """
        self.points.append(point)
        self.cont += point.grouped
