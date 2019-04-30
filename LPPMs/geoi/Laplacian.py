import math
import copy
import random
from geoprivacy.utils.DataModel import DataModel
import numpy as np

class Laplacian:
    """Laplace noise method known as Geo Indistinguishability
    Adds noise to a point using a Laplace distribution, this 
    obfuscate the point changing it's latitude and longitude coordinates 
    while maintaining extra data of the point.
    """
    
    def __init__(self, sensitivity, seed, dataModel):
        """Constructor
        Process the parameters and executes the processing immediately.
        Finally it calculate error and point loss.
        :param sensitivity: The sensitivity of the laplace distribution
        :type sensitivity: float
        :param seed: Random seed for reproducibility
        :type seed: number
        :param dataModel: DataModel to be processed
        :type dataModel: DataModel
        """
        random.seed(seed)
        self.sensitivity = sensitivity
        self.points = []
        self.model = copy.deepcopy(dataModel)
        self.dataModel2Points()
        self.applyNoise() #Processing
        self.quadraticError = self.calculateError() #Quadratic error calculation
        self.pointLoss = 0
        self.pointList2DataModel()
        
    def pointList2DataModel(self):
        """Converts a list of points formated as {lat, lon, extraData}
        To a DataModel and saves it as the method DataModel
        """
        self.newDataModel = DataModel(self.points, False) 
        
    def dataModel2Points(self):
        """Converts a DataModel to a point list"""
        self.points = self.model.layerData
        
    def calculateError(self):
        """Calculates quadratic error of the processing of the method"""
        error = 0
        for point in self.points:
            error += point['error']**2
        error = error/len(self.points)
        return error
    
    def applyNoise(self):
        """asdfasdf"""
        for point in self.points:
            oldLat = copy.copy(point['lat'])
            oldLon = copy.copy(point['lon']) 
            point['lat'] = self.laplace(point['lat'], self.sensitivity)
            point['lon'] = self.laplace(point['lon'], self.sensitivity)
            point['error'] = self.dist(oldLat, oldLon, point['lat'], point['lon'])
                
    def laplace(self, center, sensitivity):
        """Applies a laplace transform to generate a random value around the laplace distribution
        :param center: mean point of the distribution
        :param sensitivity: Laplace sensitivity
        """
        res = 1/(2*sensitivity) * math.exp(-(math.fabs(random.random() - center)/sensitivity))
        res = np.random.laplace(center, sensitivity)
        return res
    
    def dist(self, lat1, lon1, lat2, lon2):
        """Euclidean distance"""
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

