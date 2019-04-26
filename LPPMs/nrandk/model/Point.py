class Point:
    def __init__(self, lat, lon, extraData):
        self.lat = lat
        self.lon = lon
        self.extraData = extraData
    
    def __repr__(self): 
        return str(self.lat + ", " + self.lon)
        
    