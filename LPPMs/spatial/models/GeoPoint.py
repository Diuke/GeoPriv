"""
Representation of a Geographic simple point.
Consist of latitude, longitue only.
"""


class GeoPoint:
    def __init__(self, lat, lon, extra):
        self.latitude = lat
        self.longitude = lon
        self.extra = extra
        self.val = 0

    def round_lat_lon(self, decimal_digits):
        scale = float(10**decimal_digits)

        temp_lat = round(self.latitude * scale)
        temp_lon = round(self.longitude * scale)

        self.latitude = float(temp_lat/scale)
        self.longitude = float(temp_lon / scale)

    """
    Returns the id of the point to be grouped concatenating latitude and longitude.
    """
    def calc_id(self):
        self.val = str(self.latitude) + str(self.longitude)
        return self.val

    def __repr__(self):
        return str(self.latitude) + "," + str(self.longitude)
