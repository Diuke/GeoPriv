from qgis.core import *
from PyQt5.QtCore import QVariant
import copy

'''
Data model for a layer to be used
Separates the layer data and the fields and stores them into python lists for an easier use
Layer data: List of {lat, lon, extraData}
Has 2 ways to transform data, when it comes from a QgsLayer it is tranformed using features2list
when it comes from a non-layer data structre the data structure needs to have a structure as follows
c
cont is used when grouping values causing them to lose additional information and gaining several points
as a new field.
'''
class DataModel:     
    
    def log(self, msg):
        """Escribe en el log del plugin en la pestaña de resultados"""
        QgsMessageLog.logMessage(msg, level=Qgis.Info)   
    
    def __init__(self, layer, isLayer=None):  
        """Constructor
        :param layer: The data layer or data structure that have the data used to build the DataModel
        :type layer: QgsLayer or Object
        :param isLayer: Variable that defines if the incoming data structure is a layer or an object.
        :type isLayer: boolean
        """
        self.layerData = []
        self.fields = []
        self.isLayer = isLayer
        
        if isLayer == True: #When information comes from a layer the field information and layer features are extracted
            data = layer.getFeatures()
            self.setFieldData(layer.fields().names(), data)
            self.layerData = self.features2list(data)
            
        elif isLayer == False: #else it uses method2list to build a DataModel from an object
            self.layerData, self.fields = self.method2list(layer)
            
        elif isLayer == None:
            self.isLayer = False
            
            for field in layer.fields:
                if isinstance(field, QVariant):
                    tempField = field
                else:
                    tempField = copy.deepcopy(field)
                self.fields.append(tempField)
            
            for row in layer.layerData:
                tempRow = {}
                tempRow['lat'] = copy.deepcopy(row['lat'])
                tempRow['lon'] = copy.deepcopy(row['lon'])
                tempRow['extraData'] = {}
                for key, val in row['extraData'].items():
                    if isinstance(val, QVariant):
                        tempVal = val
                        tempRow['extraData'][key] = tempVal
                    else:
                        tempRow['extraData'][key] = copy.deepcopy(val)
                self.layerData.append(tempRow)
            
        
    def method2list(self, data):
        """Transform data like {lat, lon, extraData} into a DataModel
        :param data: the data to put into de DataModel
        :return: The list of the form {lat, lon, extraData}
        """
        list = []
        fields = []
        for key, val in data[0]['extraData'].items():
            if key == 'cont': 
                fields.append('size')
            else:
                fields.append(key)
                    
        for p in data:
            row = {}
            row['lat'] = p['lat']
            row['lon'] = p['lon']
            if 'cont' in p: 
                extraData = {'size': p['cont']}
            else: #if the features have other data, pass them to the model extra data.
                extraData = p['extraData']
            row['extraData'] = extraData
            list.append(row)
        return list, fields
    
    def features2list(self, data):
        """Transform data from a QGIS Layer to the DataModel
        :param data: the data to put into de DataModel
        :return: The list of que form {lat, lon, }
        """
        list = []
        for feature in data:
            row = {}
            row['lon'] = feature.geometry().asPoint().x()
            row['lat'] = feature.geometry().asPoint().y()
            extraData = {}
            for field in self.getFieldData():
                #if feature.attribute(field) != row['lon'] and feature.attribute(field) != row['lat']: 
                extraData[field] = feature.attribute(field)
            row['extraData'] = extraData
            list.append(row)
        return list
        
        
    def list2features(self, list):
        """Transform the dataModel list into a list of features to be included into a QgsLayer
        :param list: Point list
        :return: fields anf features of the data model made from list.
        """
        features = []
        fields = QgsFields()
        for i, f in enumerate(list):
            fields = QgsFields()
            for key, val in f['extraData'].items():
                fields.append(QgsField(key, QVariant.Int,'', 100))
                
            feature = QgsFeature(fields)
                
            a = feature.fields().names()
            for key, val in f['extraData'].items():
                feature.setAttribute(key, val)
                
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(f['lon'],f['lat'])))
                
            features.append(feature)
        return fields, features
    
    def getFieldData(self):
        """Gets the field list"""
        return self.fields
    
    def setFieldData(self, fields, data):
        """Sets the field list of the DataModel.
        It removes fields equal to the geographic coordinates of each feature."""
        self.fields = [] 
        for feature in data: 
            for field in fields:
                if isinstance(feature.attribute(field), float):
                    lon = feature.geometry().asPoint().x()
                    lat = feature.geometry().asPoint().y()
                    if (round(feature.attribute(field), 2) != round(lon, 2) and 
                        round(feature.attribute(field), 2) != round(lat, 2)):
                        self.fields.append(field)
                else:
                    self.fields.append(field)
            return
        
        
    