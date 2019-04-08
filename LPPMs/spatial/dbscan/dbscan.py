import csv
class DBScan:
    point_list = []
    cluster_list = []
    ready_points = []

    def __init__(self, point_list, mink):
        self.point_list = []
        self.cluster_list = []
        for p in point_list:
            if p.grouped >= mink:
                c = Cluster()
                c.add_point(p)
                self.ready_points.append(c)
            else:
                self.point_list.append(p)

    def fit(self, eps, min_size):
        taken = set()
        cont = 0
        for point in self.point_list:
            if not taken.__contains__(point):
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
        #print("all" +str(cont))

    def calculate_centroid(self):
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
    def __init__(self):
        self.lat = 0
        self.lon = 0
        self.cont = 0
        self.points = []

    def add_point(self, point):
        self.points.append(point)
        self.cont += point.grouped
