from qgis.core import *

'''
Data model for a layer to be used
Separates the layer data and the fields and stores them into python lists for an easier use
'''
class DataModel:
    
    def __init__(self, layer, isLayer):
        self.layerData = []
        self.fields = []
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
            row['lat'] = p.lat
            row['lng'] = p.lon
            extraData = {'size': p.cont}
            row['extraData'] = extraData
        return list
    
    def features2list(self, data):
        list = []
        for feature in data:
            row = {}
            row['lng'] = feature.geometry().asPoint().x()
            row['lat'] = feature.geometry().asPoint().y()
            extraData = {}
            for field in self.getFieldData():
                if feature.attribute(field) != row['lng'] and feature.attribute(field) != row['lat']: 
                    a = feature.attribute(field)
                    extraData[field] = feature.attribute(field)
            row['extraData'] = extraData
            list.append(row)
        return list
        
        
    def list2features(self, list):
        features = []
        for i, f in enumerate(list):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(f['lng'],f['lat'])))
            for key, val in f['extraData'].items():
                feature.setAttribute(key, val)
            features.append(feature)
        return features
    
    def getFieldData(self):
        return self.fields
    
    def setFieldData(self, fields):
        self.fields = fields
        
    
        
        
    