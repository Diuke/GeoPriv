# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Geopriv
                                 A QGIS plugin
 A set of location privacy tools for geographic data.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-01-24
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Juan Duque, Angelly Pugliese
        email                : pjduque@uninorte.edu.co, angellyp@uninorte.edu.co
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QTableWidget, QTableWidgetItem
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import * 
# Import the code for the dialog
from .geoprivacy_dialog import GeoprivDialog
import os.path
import traceback
import sys

#custom classes
from .utils.DataModel import DataModel
from .LPPMs.spatial.Spatial import Spatial
from .LPPMs.nrandk.NRandK import NRandK
from .LPPMs.geoi.Laplacian import Laplacian

class Geopriv:
    """QGIS Plugin Implementation."""
    
    # Working layer of the plugin
    layer = None

    #previewDataTable
    previewDataTable = None
    
    #new layer data
    layerData = None
    
    #Complete original layer
    completeLayerData = None
    
    
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Geopriv_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geoprivacy Plugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        self.algorithmDict = {0: None, 1: 'K-Means', 2: 'DBSCAN'}

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Geopriv', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/geoprivacy/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Geoprivacy'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Geoprivacy Plugin'),
                action)
            self.iface.removeToolBarIcon(action)
            
    def createNewLayer(self, newLayerName, dataModel):
        """Creates a new layer with a specified name and from a DataModel
        :param newLayerName: Name for the created layer.
        :type newLayerName: str
        :param dataModel: DataModel from which the new layer will be constructed.
        :type dataModel: DataModel
        """
        #PARAMETERS FOR THE NEW LAYER (geographic projection matches)
        layerCrs = self.layer.sourceCrs().authid()
        uri = "Point?crs="+layerCrs
        name = newLayerName
        provider = 'memory' #Creates the layer in-memory
         
        #CREATE NEW TEMPORARY LAYER WITH THE ABOVE PARAMETERS
        newLayer = self.iface.addVectorLayer(uri, name, provider) 
        pr = newLayer.dataProvider()
        
        #FETCHING FIELDS AND FEATURES
        fields, features = dataModel.list2features(dataModel.layerData)
        
        #ADDING AND UPDATING THE FIELDS
        pr.addAttributes(fields)
        newLayer.updateFields()
        
        #ADDING AND UPDATING THE FEATURES 
        pr.addFeatures(features)
        newLayer.updateExtents()
        
    
    def configSelectedLayerComboBox(self):
        """Aplies a filter to only show Point geometry layers in the select layer combo box """
        selectLayer = self.dlg.layerSelect
        layers = []
        selectLayer.setAllowEmptyLayer(True) 
        project_layers = QgsProject.instance().layerStore().mapLayers()
        for name, l in project_layers.items():
            if isinstance(l, QgsVectorLayer):
                type = l.wkbType()
                if type != 1:
                    layers.append(l)
            else:
                layers.append(l)
        #set the filtered layers for the combo box
        selectLayer.setExceptedLayerList(layers)
        self.setLayer()
        self.dlg.layerSelect.currentIndexChanged.connect(self.setLayer)
        
    def setLayer(self): 
        """Set the selected layer to the layer global model and fetch the data to the GUI data preview tab"""
        self.layer = None
        if self.dlg.layerSelect.currentLayer() != None:
            self.layer = self.dlg.layerSelect.currentLayer()
            self.populatePreviewDataTable(self.layer)
        
    def populatePreviewDataTable(self, layer):
        """Writes the data from layer to the GUI Data Preview tab
       :param layer: the layer to be processed
       :type layer: QgsLayer 
        """
        data = DataModel(layer, True)
        rowCount = 100 if len(data.layerData) >= 100 else len(data.layerData)
        colCount = len(data.fields) + 2
        self.previewDataTable.setRowCount(rowCount)
        self.previewDataTable.setColumnCount(colCount)
        self.previewDataTable.setHorizontalHeaderItem(0, QTableWidgetItem("Latitude"))
        self.previewDataTable.setHorizontalHeaderItem(1, QTableWidgetItem("Longitude"))
        
        #Set the headers of the table
        for i, field in enumerate(data.fields):
            self.previewDataTable.setHorizontalHeaderItem(i+2, QTableWidgetItem(field))
            
        #Populates the table with latitude, longitude and extra data
        for i in range(0, rowCount):
            for j in range(0, colCount): 
                info = ""
                if j == 0:
                    info = data.layerData[i]['lat']
                elif j == 1:
                    info = data.layerData[i]['lon']
                else:
                    info = data.layerData[i]['extraData'][data.fields[j-2]]
                    
                self.previewDataTable.setItem(i, j, QTableWidgetItem(str(info)))
        self.data = data
                
    def log(self, msg):
        """Escribe en el log del plugin en la pestaña de resultados"""
        # QgsMessageLog.logMessage(msg, level=Qgis.Info)
        self.resultsLog.addItem(msg)
        
    def processNRankdK(self):
        """Executes the NRandK protection mechanism."""
        self.goToResultsTab()
        
        #Parameter values assingment
        self.log("Starting NRandK.")
        gridPrecision = self.nrandkGridPrecision.value()
        n = self.nrandkN.value()
        k = self.nrandkK.value()
        sRadius = self.nrandkSRadius.value()
        lRadius = self.nrandkLRadius.value()
        randomSeed = self.nrandkRandomSeed.value()
        
        #Validation
        hasError = False
        if gridPrecision == 0:
            self.log("Grid decimal precision must be greater than 0")
            hasError = True
        elif n == 0:
            self.log("Number of points generated (N) must be greater than 0")
            hasError = True
        elif k == 0:
            self.log("Minimum points (K) must be greater than 0")
            hasError = True
        elif sRadius == 0:
            self.log("Small radius must be greater than 0")
            hasError = True
        elif lRadius == 0:
            self.log("Large radius must be greater than 0")
            hasError = True
        elif lRadius <= sRadius:
            self.log("Large radius must be greater than Small Radius")
            hasError = True
        
        self.log("Variables loaded")            
        self.log("Starting clustering.")  
        
        #Processing
        try:
            newData = NRandK(k, n, gridPrecision, sRadius, lRadius, randomSeed, self.data)
            self.dlg.QError.setText(str(newData.quadraticError))
            self.dlg.pointLoss.setText(str(newData.pointLoss))
        except Exception as err:
            self.log("An error occurred during processing")
            self.log(str(err))
            self.log(str(traceback.format_exc()))
        else:
            self.log("NRandK processing was successful.")
            self.log("Creating new temporal layer.")
        #Layer generation
            self.createNewLayer("NRandK", newData.newDataModel)
            self.log("Temporal layer NRandK created.")
            self.log("Quadratic Error: " + str(newData.quadraticError))
            
    def processGeoi(self):
        """Exectures Geo Indistinguishability protection mechanism"""
        self.goToResultsTab()
        
        #Parameter values assingment
        self.log("Starting spatial clustering.")
        sensitivity = self.geoiSensitivity.value()
        randomSeed = self.geoiRandomSeed.value()
        
        #Validations
        hasError = False
        if sensitivity == 0:
            self.log("Sensitivity must be greater than 0")
            hasError = True
        
        self.log("Variables loaded")            
        self.log("Starting clustering.")   
        
        #Processing
        try:
            newData = Laplacian(sensitivity, randomSeed, self.data)
            self.dlg.QError.setText(str(newData.quadraticError))
            self.dlg.pointLoss.setText(str(newData.pointLoss)) 
        except Exception as err:
            self.log("An error occurred during processing")
            self.log(str(err))
            self.log(str(traceback.format_exc()))
        else:
            self.log("Laplace Noise processing was successful.")
            self.log("Creating new temporal layer.")
        #Layer generation
            name = "Laplace"
            self.createNewLayer(name, newData.newDataModel)
            self.log("Temporal layer Laplace created.")
            self.log("Quadratic Error: " + str(newData.quadraticError))
    
    def processSpatial(self):
        """Executes spatial clustering protection mechanism"""
        self.goToResultsTab()
        #Parameter values assingment
        self.log("Starting spatial clustering.")
        params = {}
        params['minK'] = self.minK.value()
        params['algorithm'] = self.algorithmDict[self.algorithmSelect.currentIndex()]
        params['gridPrecision'] = self.gridPrecision.value()
        if params['algorithm'] is not None:
            if params['algorithm'] == 'K-Means':
                params['kmeans_k'] = self.numberOfClusters.value()
                params['kmeans_seed'] = self.randomSeed.value()
            elif params['algorithm'] == 'DBSCAN':
                params['dbscan_r'] = self.radius.value()
                params['dbscan_minSize'] = self.minClusterSize.value()
        
        #Validations
        hasError = False
        if params['minK'] == 0:
            hasError = True
            self.log("Minimum K must be greater than 0")
        if params['algorithm'] == 0:
            self.log("You must select an algorithm.")
            hasError = True
        if params['gridPrecision'] == 0:
            self.log("Grid decimal precision must be greater than 0")
            hasError = True
        if params['algorithm'] == 'K-Means':
            if params['kmeans_k'] == 0:
                self.log("Number of clusters must be greater than 0")
                hasError = True
        elif params['algorithm'] == 'DBSCAN':
            if params['dbscan_r'] == 0:
                self.log("Radius must be greater than 0")
                hasError = True 
            if params['dbscan_minSize'] == 0:
                self.log("DBSCAN Minimum cluster size must be greater than 0")
                hasError = True
        if hasError:
            return 
        
        self.log("Variables loaded")            
        self.log("Starting clustering.")   
        
        #Processing
        try:
            newData = Spatial(self.data, params)
            self.dlg.QError.setText(str(newData.quadraticError))
            self.dlg.pointLoss.setText(str(newData.pointLoss))
        except Exception as err:
            self.log("An error occurred during processing")
            self.log(str(err))
            self.log(str(traceback.format_exc()))
        else:
            self.log(params['algorithm'] + " processing was successful.")
            self.log("Creating new temporal layer.")
        #Layer generation
            name = self.algorithmDict[self.algorithmSelect.currentIndex()]
            self.createNewLayer(name, newData.newDataModel)
            self.log("Temporal layer " + params['algorithm'] + " created.")
            self.log("Quadratic Error: " + str(newData.quadraticError))
        
    def goToResultsTab(self):
        """Opens the results tab. Used to show results after processing"""
        last = self.tabs.count()
        self.tabs.setCurrentIndex(last-1)

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = GeoprivDialog()
            #Events are added here to be loaded only once
            self.dlg.processSpatialButton.clicked.connect(self.processSpatial)
            self.dlg.processNRandKButton.clicked.connect(self.processNRankdK)
            self.dlg.processGeoiButton.clicked.connect(self.processGeoi)
        
        #Loading general controls
        self.previewDataTable = self.dlg.previewDataTable 
        self.configSelectedLayerComboBox()
        self.resultsLog = self.dlg.resultsLog
        self.tabs = self.dlg.pluginTabs
        
        #NRandK Form Controls
        self.nrandkGridPrecision = self.dlg.nrandkGridPrecision
        self.nrandkN = self.dlg.nrandkN
        self.nrandkK = self.dlg.nrandkK
        self.nrandkSRadius = self.dlg.nrandkSRadius
        self.nrandkLRadius = self.dlg.nrandkLRadius
        self.nrandkRandomSeed = self.dlg.nrandkRandomSeed
        
        #GeoI Form Controls
        self.geoiSensitivity = self.dlg.geoiSensitivity
        self.geoiRandomSeed = self.dlg.geoiRandomSeed
        
        #Spatial Form Controls
        #Globals
        self.minK = self.dlg.minKGlobal
        self.algorithmSelect = self.dlg.algorithmSelect
        self.gridPrecision = self.dlg.gridPrecision
        #K-Means
        self.numberOfClusters = self.dlg.clustersNumber
        self.randomSeed = self.dlg.randomSeed
        #DBSCAN
        self.radius = self.dlg.radius
        self.minClusterSize = self.dlg.minClusterSize
        
        
        # show the dialog 
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        print("now running")
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

