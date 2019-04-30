# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Geopriv class from file Geopriv.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geoprivacy import Geopriv
    return Geopriv(iface)
