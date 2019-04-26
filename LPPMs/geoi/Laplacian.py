import math
import copy
import random
from geoprivacy.utils.DataModel import DataModel
import numpy as np

class Laplacian:
    
    def __init__(self, sensitivity, seed, dataModel):
        random.seed(seed)
        self.sensitivity = sensitivity
        self.points = []
        self.model = copy.deepcopy(dataModel)
        self.dataModel2Points()
        self.applyNoise()
        self.quadraticError = self.calculateError()
        self.pointLoss = 0
        self.pointList2DataModel()
        
    def pointList2DataModel(self):
        self.newDataModel = DataModel(self.points, False) 
        
    def dataModel2Points(self):
        self.points = self.model.layerData
        
    def calculateError(self):
        error = 0
        for point in self.points:
            error += point['error']**2
        error = error/len(self.points)
        return error
    
    def applyNoise(self):
        for point in self.points:
            oldLat = copy.copy(point['lat'])
            oldLon = copy.copy(point['lon']) 
            point['lat'] = self.laplace(point['lat'], self.sensitivity)
            point['lon'] = self.laplace(point['lon'], self.sensitivity)
            point['error'] = self.dist(oldLat, oldLon, point['lat'], point['lon'])
                
    def laplace(self, center, sensitivity):
        res = 1/(2*sensitivity) * math.exp(-(math.fabs(random.random() - center)/sensitivity))
        res = np.random.laplace(center, sensitivity)
        return res
    
    def dist(self, lat1, lon1, lat2, lon2):
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

