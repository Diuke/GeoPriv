import math
import random
import copy
from geoprivacy.utils.DataModel import DataModel
from matplotlib.cbook import maxdict

class NRandK:
    def __init__(self, k, n, gridSize, sRadius, lRadius, seed, dataModel):
        random.seed(seed)
        self.k = k
        self.n = 4
        self.gridSize = gridSize
        self.sRadius = sRadius
        self.lRadius = lRadius
        self.model = copy.deepcopy(dataModel)
        self.dataModel2Points()
        self.gridify()
        self.process()
        self.pointList2DataModel()
        self.quadraticError = self.calculateError()
        self.pointLoss = 0
        
    def pointList2DataModel(self):
        self.newDataModel = DataModel(self.points, False) 
        
    def dataModel2Points(self):
        self.points = self.model.layerData
    
    def printPoints(self):
        for point in self.points:
            print(str(point.lat) + str(point.lon))
        
    def gridify(self):
        grids = {}
        for point in self.points:
            temp_lat = round(point['lat'] * (10**self.gridSize))
            temp_lon = round(point['lon'] * (10**self.gridSize))
                
            temp_lat = float(temp_lat/(10**self.gridSize))
            temp_lon = float(temp_lon / (10**self.gridSize))
            
            id = str(temp_lat) + str(temp_lon)
            point['id'] = id
            if id in grids.keys():
                grids[id] += 1  
            else:
                grids[id] = 1
        
        for point in self.points:
            point['radius'] = self.sRadius if grids[point['id']] >= self.k else self.lRadius
        
    def process(self):
        for point in self.points:
            maxLat = 0
            maxlon = 0
            maxDist = -99999999
            for i in range(0, self.n):
                tempLat, templon = self.generateRandomPoint(point['radius'], point)
                dist = self.dist(point['lat'], point['lon'], tempLat, templon)
                if dist > maxDist:
                    maxDist = dist
                    maxLat = tempLat
                    maxlon = templon 
            point['lat'] = maxLat
            point['lon'] = maxlon
            point['error'] = maxDist
                
    def generateRandomPoint(self, radius, point):
        randRadius = radius * math.sqrt(random.random())

        randLat = (randRadius * math.cos(2*math.pi*random.random())) + point['lat']
        randlon = (randRadius * math.sin(2*math.pi*random.random())) + point['lon']
        return randLat, randlon
    
    def calculateError(self):
        error = 0
        for point in self.points:
            error += point['error']**2
        error = error/len(self.points)
        return error
    
    def dist(self, lat1, lon1, lat2, lon2):
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        