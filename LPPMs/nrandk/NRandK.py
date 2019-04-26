import math
import random
from geoprivacy.utils.DataModel import DataModel

class NRandK:
    def __init__(self, k, n, gridSize, dataModel):
        self.k = k
        self.n = 4
        self.gridSize = gridSize
        self.sRadius = 0.001
        self.lRadius = 0.01
        self.model = dataModel
        self.dataModel2Points()
        self.gridify()
        self.process()
        self.pointList2DataModel()
        
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
                if self.dist(point['lat'], point['lon'], tempLat, templon) > maxDist:
                    maxLat = tempLat
                    maxlon = templon 
            point['lat'] = maxLat
            point['lon'] = maxlon
                
    def generateRandomPoint(self, radius, point):
        randRadius = random.uniform(0, radius)
        print(randRadius)
        randLat = (randRadius * math.cos(random.uniform(0,2*math.pi))) + point['lat']
        randlon = (randRadius * math.sin(random.uniform(0,2*math.pi))) + point['lon']
        return randLat, randlon
    
    def dist(self, lat1, lon1, lat2, lon2):
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        