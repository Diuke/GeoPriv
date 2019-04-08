"""
Representation of a Geographic simple point.
Consist of latitude, longitue only.
"""


class GeoPoint:
    def __init__(self, lat, lon, scale, extra):
        self.latitude = lat
        self.longitude = lon
        self.extra = extra
        self.val = 0
        self.scale = float(10**scale)        

    """
    Returns the id of the point to be grouped concatenating latitude and longitude.
    """
    def calc_id(self):
        temp_lat = round(self.latitude * self.scale)
        temp_lon = round(self.longitude * self.scale)

        temp_lat = float(temp_lat/self.scale)
        temp_lon = float(temp_lon / self.scale)
        self.val = str(temp_lat) + str(temp_lon)
        return self.val

    def __repr__(self):
        return str(self.latitude) + "," + str(self.longitude)
