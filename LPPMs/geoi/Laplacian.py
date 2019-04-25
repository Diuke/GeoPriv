import math
import random
from models.Point import Point
import numpy as np

class Laplacian:
    
    def __init__(self, sensitivity, points):
        random.seed(0)
        self.sensitivity = sensitivity
        self.pointList = []
        for point in points:
            self.pointList.append(Point(point['lat'], point['lng'], point['extraData']))
        self.applyNoise()
        self.printPoints()
    
    def applyNoise(self):
        for point in self.pointList:
            point.lat = self.laplace(point.lat, self.sensitivity)
            point.lon = self.laplace(point.lon, self.sensitivity)
                
    def laplace(self, center, sensitivity):
        res = 1/(2*sensitivity) * math.exp(-(math.fabs(random.random() - center)/sensitivity))
        res = np.random.laplace(center, sensitivity)
        return res
    
    
    def printPoints(self):
        for point in self.pointList:
            print(str(point.lat) + ", " + str(point.lon))
        
points = [
    {'lat': 10.9183063, 'lng': -74.8106452, 'extraData': {}},
    {'lat': 10.9425505, 'lng': -74.7687247, 'extraData': {}},    
]
l = Laplacian(0.001, points)
