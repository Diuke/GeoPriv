class GeoPoint:
    """Representation of a Geographic simple point.
    Consist of latitude, longitue only.
    """
    def __init__(self, lat, lon, scale, extra):
        """Constructor
        :param lat: latitude
        :type lat: float
        :param lon: longitude
        :type lon: float
        :param scale: Number of decimal points to be considered from lat and lon
        :type scale: number
        :param extra: Any extra data to be added to the point
        :type extra: Object
        """
        self.latitude = lat
        self.longitude = lon
        self.extra = extra
        self.val = 0
        self.scale = float(10**scale)        

    
    def calc_id(self):
        """
        Returns the id of the point to be grouped concatenating latitude and longitude.
        """
        temp_lat = round(self.latitude * self.scale)
        temp_lon = round(self.longitude * self.scale)

        temp_lat = float(temp_lat/self.scale)
        temp_lon = float(temp_lon / self.scale)
        self.val = str(temp_lat) + str(temp_lon)
        return self.val