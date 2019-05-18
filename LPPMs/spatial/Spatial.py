import math
import copy
from .dbscan import dbscan
from .kmeans import kmeans
from .models import GridPoint as gp 
from GeoPriv.utils.DataModel import DataModel 
import math

#import matplotlib.pyplot as plt
"""
Spatial clustering privacy protection mechanism.
Uses Kmeans and DBSCAN as spatial clustering methods after applying gridification to spatial points.
"""
class Spatial:
    
    """
    Initialization of
    """
    def __init__(self, dataModel, params):
        """Constructor
        Assign parameters depending on the selected algorithm
        :param dataModel: The DataModel to be processed.
        :param params: Object containing necessary parameters for each method.
        """
        # The Data Model is deep copied to be editable separately from the original Data Model
        #self.model = copy.deepcopy(dataModel)
        self.model = DataModel(dataModel) #Deep copies the datamodel to be editable
        self.quadraticError = 0
        
        # The params parameter brings all necesary parameters for both spatial clustering methods.
        self.minK = params['minK']
        self.algorithm = params['algorithm']
        self.dec_points = params['gridPrecision']
        
        # Parameters for KMeans
        if self.algorithm == 'K-Means':
            self.kmeans_k = params['kmeans_k']
            self.kmeans_seed = params['kmeans_seed']
            
        # Parameters for DBSCAN
        elif self.algorithm == 'DBSCAN':
            self.dbscan_r = params['dbscan_r']
            self.dbscan_minSize = params['dbscan_minSize']
        
        # Executes the spatial clustering algorithm. None if 
        result = self.execute()
        if result != None:
            self.clusters = result.cluster_list
        else:
            return
        
        times = 0
        
        while not self.correct_clusters(): #groups clusters that don't comply with minumum K with closer cluster.
            if times > 100: #if the algorithm takes more than 100 steps to complete is not convergent.
                raise Exception("The algorithms is taking too much time to finish (Clustering is not convergent)")
            times += 1
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
                    self.clusters[min_index].points.extend(cluster.points)
                    self.clusters.remove(cluster)
          
        self.pointList2DataModel() #Convert DataModel to point list
        self.quadraticError = self.calculateError() #Calculates error
        self.pointLoss = self.calculatePointLoss() #Calculates point loss
        
    def calculateError(self):
        """Calculates quadratic error of the points in each cluster and its original point"""
        if self.newDataModel is None or self.model is None:
            return -1
        
        error = 0
        cont = 0
        for cluster in self.clusters:
            for point in cluster.points:
                cont += 1
                dist = math.sqrt((point.lat-cluster.lat)**2 + (point.lon-cluster.lon)**2)
                error += dist**2
        error = error / cont
        return error
    
    def calculatePointLoss(self):
        """Calculates how many points were removed during clustering"""
        if self.newDataModel is None or self.model is None:
            return 0
    
        contOriginal = 0
        contProcessed = 0
        for cluster in self.clusters:
            contOriginal += cluster.cont
        contProcessed = len(self.model.layerData)
        return math.fabs(contOriginal - contProcessed)
    
    def setPointList(self):
        """Converts the data from layer to a point list"""
        self.point_list = []
        for p in self.model.layerData:
            self.point_list.append([p['lat'], p['lon'], p['extraData']])
            
    def pointList2DataModel(self):
        """Converts list of points to a DataModel"""
        clusters4DataModel = []
        for cluster in self.clusters:
            clusters4DataModel.append({
                'lat': cluster.lat,
                'lon': cluster.lon,
                'extraData': {'cont': cluster.cont}
            })
        self.newDataModel = DataModel(clusters4DataModel, False)
        
    def cluster_distance(self, c1, c2):
        """Calculate the distance between two clusters.
        :param c1: Cluster 1
        :param c2: Cluster 2
        """
        dist = float(math.sqrt((c1.lat-c2.lat)**2 + (c1.lon-c2.lon)**2))
        return dist
        
    def correct_clusters(self):
        """Checks if every cluster is correct and has a minumum of minK points (globaly)"""
        for cluster in self.clusters:
            if cluster.cont < self.minK:
                return False
        return True
        
    def execute(self):
        """Executes the specified clustering algorithm and return the list of clusters."""
        #0: lat, 1: lon
        self.setPointList()
        
        grid_list = gp.GridPoint.gridify(self.point_list, self.dec_points)
        
        if self.algorithm == 'K-Means':
            
            data = kmeans.Kmeans(grid_list, self.minK, self.kmeans_seed)
            data.calculate_clusters(self.kmeans_k) 
            
        elif self.algorithm == 'DBSCAN':
            data = dbscan.DBScan(grid_list, self.minK)
            data.fit(self.dbscan_r, self.dbscan_minSize)
            
        else: 
            data = None
        
        return data
            
