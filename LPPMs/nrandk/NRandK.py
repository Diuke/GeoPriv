import math
import random
import copy
from geoprivacy.utils.DataModel import DataModel
from matplotlib.cbook import maxdict

class NRandK:
    """NRandK location privacy method
    Generates random points around the original points according to how many other points are around
    it after performing a gridification. 
    """
    def __init__(self, k, n, gridSize, sRadius, lRadius, seed, dataModel):
        """Constructor
        :param k: Minimum of points to use the Large radius
        :param n: Number of points generated to select only one
        :param gridSize: Number of decimals taken for the gridification
        :param sRadius: Small radius for the random points
        :param lRadius: Large radius for the random points 
        :param seed: Random seed for reproducibility
        :param dataModel: DataModel to be processed 
        """
        random.seed(seed)
        self.k = k
        self.n = 4
        self.gridSize = gridSize
        self.sRadius = sRadius
        self.lRadius = lRadius
        self.model = copy.deepcopy(dataModel) #Deep copies the datamodel to be editable
        self.dataModel2Points()
        self.gridify() #applies gridification first
        self.process() #Process data secont
        self.pointList2DataModel()
        self.quadraticError = self.calculateError() #calculates quadratic error
        self.pointLoss = 0
        
    def pointList2DataModel(self):
        """Converts a list of points formated as {lat, lon, extraData}
        To a DataModel and saves it as the method DataModel
        """
        self.newDataModel = DataModel(self.points, False) 
        
    def dataModel2Points(self):
        """Converts a DataModel to a point list"""
        self.points = self.model.layerData

    def gridify(self):
        """Build a virtual grid over the points and assign each point a grid cell
        by its truncated coordinates.
        """
        grids = {}
        for point in self.points:
            temp_lat = round(point['lat'] * (10**self.gridSize)) #truncates latitude
            temp_lon = round(point['lon'] * (10**self.gridSize)) #truncates longitude
                
            temp_lat = float(temp_lat/(10**self.gridSize))
            temp_lon = float(temp_lon / (10**self.gridSize))
            
            id = str(temp_lat) + str(temp_lon) #calculates id as the concatenation of truncated coordinates
            point['id'] = id #assign the grid
            if id in grids.keys():
                grids[id] += 1
            else:
                grids[id] = 1
        
        for point in self.points:
            point['radius'] = self.sRadius if grids[point['id']] >= self.k else self.lRadius
        
    def process(self):
        """Applies the NRandK location privacy method.
        Using the grid generated, if the point is surrounded by more than k points it uses a small
        radius to add noise, otherwise it uses the large radius.
        Generates n random points around that radius and select the farthest.
        """
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
            point['error'] = maxDist #calculates error instantly
                
    def generateRandomPoint(self, radius, point):
        """Generate a random point inside a circle of center point and radius radius
        :param radius: Radius of the generator circle
        :param point: The center of the point from which the point will be chosen
        """
        randRadius = radius * math.sqrt(random.random())

        randLat = (randRadius * math.cos(2*math.pi*random.random())) + point['lat']
        randlon = (randRadius * math.sin(2*math.pi*random.random())) + point['lon']
        return randLat, randlon
    
    def calculateError(self):
        """Calculates quadratic error of the new and old points"""
        error = 0
        for point in self.points:
            error += point['error']**2
        error = error/len(self.points)
        return error
    
    def dist(self, lat1, lon1, lat2, lon2):
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
        