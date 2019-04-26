from qgis.core import *
from PyQt5.QtCore import QVariant

'''
Data model for a layer to be used
Separates the layer data and the fields and stores them into python lists for an easier use
Layer data: List of {lat, long, extraData}
'''
class DataModel:
    
    def __init__(self, layer, isLayer):  
        self.layerData = []
        self.fields = []
        self.isLayer = isLayer
        if isLayer: 
            self.setFieldData(layer.fields().names())
            data = layer.getFeatures()
            self.layerData = self.features2list(data)
            #self.list2features(self.layerData)
        else: 
            self.layerData = self.method2list(layer)
        
    def method2list(self, data):
        list = []
        for p in data:
            row = {}
            row['lat'] = p['lat']
            row['lon'] = p['lon']
            if hasattr(p, 'cont'):
                extraData = {'size': p.cont}
            else:
                extraData = p['extraData']
            row['extraData'] = extraData
            list.append(row)
        return list
    
    def features2list(self, data):
        list = []
        for feature in data:
            row = {}
            row['lon'] = feature.geometry().asPoint().x()
            row['lat'] = feature.geometry().asPoint().y()
            extraData = {}
            for field in self.getFieldData():
                #if feature.attribute(field) != row['lon'] and feature.attribute(field) != row['lat']: 
                a = feature.attribute(field)
                extraData[field] = feature.attribute(field)
            row['extraData'] = extraData
            list.append(row)
        return list
        
        
    def list2features(self, list):
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
        return self.fields
    
    def setFieldData(self, fields):
        self.fields = fields
        
    
        
        
    