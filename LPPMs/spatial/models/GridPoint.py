import math
from . import GeoPoint

class GridPoint:
    """
    Abstraction of a gridified point.
    The resulting points after gridification. 
    GridPoints have latitude, longitude and the number of points grouped.
    """
    def __init__(self, lat, lon, id, extra):
        """Constructor
        :param lat: latitude
        :type lat: float
        :param lon:longitude
        :type lon: float
        :param id: concatenation of latitude and longitude after truncation
        :type id: str
        :param extra: extra data of the point
        :type extra: dict
        """
        self.id = id
        self.lat = lat
        self.lon = lon
        self.extra = extra
        self.grouped = 0

    @staticmethod
    def gridify(lista, digits):
        """Gridification method
        Converts GeoPoints into GridPoints using the latitude and longitude.
        Truncates latitude and longitude to the digits specified and builds a virtual grid using the truncated coordinates.
        Returns a list of GridPoints based on the list of GeoPoints received as the parameter lista.
        :param lista:
        :type lista: List
        :param digits: Decimal digits for truncation
        :type digits: number
        """
        geo_point_list = []
        max_lon = 0
        min_lon = 0
        for point in lista:
            temp_lat = float(point[0])
            temp_lon = float(point[1])
            temp_extra = point[2]
            gp = GeoPoint.GeoPoint(temp_lat, temp_lon, digits, temp_extra)
            #gp.round_lat_lon(digits)
            geo_point_list.append(gp)
            if temp_lon > max_lon:
                max_lon = temp_lon
            if temp_lon < min_lon:
                min_lon = temp_lon

        grid_dict = {}
        for point in geo_point_list:
            grid_point = GridPoint(point.latitude, point.longitude, point.calc_id(), point.extra)
            # print(grid_point.id)
            if  grid_point.id not in grid_dict:
                grid_dict[grid_point.id] = grid_point
            else: 
                grid_dict[grid_point.id].lat += grid_point.lat
                grid_dict[grid_point.id].lon += grid_point.lon
            grid_dict[grid_point.id].grouped += 1

        grid_list = []
        for point in grid_dict.values():
            point.lat = point.lat / point.grouped
            point.lon = point.lon / point.grouped   
            grid_list.append(point)
            #print(str(point.lat) + "," + str(point.lon) + "," + str(point.grouped))
        return grid_list

    def calc_distance(self, lat, lon):
        """
        Euclid distance between 2 GridPoints
        :param lat: other point latitude
        :type lat: float
        :param lon: other point longitude
        :type lon: float
        """ 
        dist = float(math.sqrt((self.lat - lat)**2 + (self.lon - lon)**2))
        return dist
