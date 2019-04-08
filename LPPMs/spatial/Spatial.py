import math
from .utils import error
from .dbscan import dbscan
from .kmeans import kmeans
from .models import GridPoint as gp 
from geoprivacy.utils.DataModel import DataModel

#import matplotlib.pyplot as plt

class Spatial:
    
    def __init__(self, dataModel, params):
        self.model = dataModel
        self.minK = params['minK']
        #self.minK = 10
        self.algorithm = params['algorithm']
        #self.algorithm = 'K-Means'
        self.dec_points = params['gridPrecision']
        #self.dec_points = 3
        
        if self.algorithm == 'K-Means':
            self.kmeans_k = params['kmeans_k']
            #self.kmeans_k = 20
            self.kmeans_seed = params['kmeans_seed']
            #self.kmeans_seed = 1
        elif self.algorithm == 'DBSCAN':
            self.dbscan_r = params['dbscan_r']
            #self.dbscan_r = 10**(-1)
            self.dbscan_minSize = params['dbscan_minSize']
            #self.dbscan_minSize = 5
        
        result = self.execute()
        if result != None:
            self.clusters = result.cluster_list
        else:
            return
        
        while not self.correct_clusters():
            for cluster in self.clusters:
                if cluster.cont < self.minK:
                    min_dist = float('inf')
                    min_cluster = None
                    for i, cluster2 in enumerate(self.clusters):
                        if cluster != cluster2:
                            distance = self.cluster_distance(cluster, cluster2)
                            if distance < min_dist:
                                min_dist = distance
                                min_index = i
                    self.clusters[min_index].cont += cluster.cont
                    self.clusters.remove(cluster)
          
        self.pointList2DataModel()
        
    
    def setPointList(self):
        self.point_list = []
        for p in self.model.layerData:
            self.point_list.append([p['lat'], p['lng'], p['extraData']])
            
    def pointList2DataModel(self):
        self.newDataModel = DataModel(self.clusters, False)
        
    def cluster_distance(self, c1, c2):
        dist = float(math.sqrt((c1.lat - c2.lat)**2 + (c1.lon - c2.lon)**2))
        return dist
        
    def correct_clusters(self):
        for cluster in self.clusters:
            if cluster.cont < self.minK:
                return False
        return True
        
    def execute(self):
        #0: lat, 1: lng
        self.setPointList()
        #print(len(point_list))
        
        grid_list = gp.GridPoint.gridify(self.point_list, self.dec_points)
        #print(len(grid_list))
        #print(grid_list)
        #print(grid_list[0].calc_distance(grid_list[1].lat, grid_list[1].lon))
        if self.algorithm == 'K-Means':
            
            data = kmeans.Kmeans(grid_list, self.minK, self.kmeans_seed)
            data.calculate_clusters(self.kmeans_k)
            #err = error.error(data.cluster_list)
            #print(err) 
            print(data)
            
        elif self.algorithm == 'DBSCAN':
            data = dbscan.DBScan(grid_list, self.minK)
            data.fit(self.dbscan_r, self.dbscan_minSize)
            #err = error.error(data.cluster_list)
            #print(err)
            print(data)
            
        else: 
            data = None
        
        return data
            
