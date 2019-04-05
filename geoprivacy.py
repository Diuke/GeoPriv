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
        email                : pjduque@uninorte.edu.co
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

#custom classes
from .utils.DataModel import DataModel


class Geopriv:
    """QGIS Plugin Implementation."""
    
    # Working layer of the plugin
    layer = None

    #previewDataTable
    previewDataTable = None
    
    #de la forma lat, lng, data
    layerData = None
    
    #Datos completos en su formato original
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
            self.iface.addPluginToMenu(
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
            self.iface.removePluginMenu(
                self.tr(u'&Geoprivacy Plugin'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def configSelectedLayerComboBox(self):
        selectLayer = self.dlg.layerSelect
        layers = []
        selectLayer.setAllowEmptyLayer(False) 
        project_layers = QgsProject.instance().layerStore().mapLayers()
        for name, l in project_layers.items():
            if isinstance(l, QgsVectorLayer):
                type = l.geometryType()
                b = type == QgsWkbTypes.PointGeometry
                if not (type == QgsWkbTypes.Point or type == QgsWkbTypes.PointGeometry):
                    layers.append(l)
            else:
                layers.append(l)
        
        selectLayer.setExceptedLayerList(layers)
        self.setLayer()
        

    def alerting(self):
        self.log("Procesando")
        
    def setLayer(self): 
        self.layer = self.dlg.layerSelect.currentLayer()
        self.populatePreviewDataTable(self.layer)
        
    def populatePreviewDataTable(self, layer):
        data = DataModel(layer)
        rowCount = 100 if len(data.layerData) >= 100 else len(data.layerData)
        colCount = len(data.fields) + 2
        self.previewDataTable.setRowCount(rowCount)
        self.previewDataTable.setColumnCount(colCount)
        self.previewDataTable.setHorizontalHeaderItem(0, QTableWidgetItem("Latitude"))
        self.previewDataTable.setHorizontalHeaderItem(1, QTableWidgetItem("Longitude"))
        
        for i, field in enumerate(data.fields):
            self.previewDataTable.setHorizontalHeaderItem(i+2, QTableWidgetItem(field))
            
        for i in range(0, rowCount):
            for j in range(0, colCount):
                info = ""
                if j == 0:
                    info = data.layerData[i]['lat']
                elif j == 1:
                    info = data.layerData[i]['lng']
                else:
                    info = data.layerData[i]['extraData'][data.fields[j-2]]
                    
                self.previewDataTable.setItem(i, j, QTableWidgetItem(str(info)))
                
    def log(self, msg):
        QgsMessageLog.logMessage(msg, level=Qgis.Info)
        

    def run(self):
        """Run method that performs all the real work"""
 
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = GeoprivDialog()
            
        
        self.previewDataTable = self.dlg.previewDataTable 
        self.configSelectedLayerComboBox()
        
        self.minK = self.dlg.minKGlobal
        self.algorithmSelect = self.dlg.algorithmSelect
        self.gridPrecision = self.dlg.gridPresicion
        self.numberOfClusters = self.dlg.clustersNumber
        self.randomSeed = self.dlg.randomSeed
        self.radius = self.dlg.radius
        self.minClusterSize = self.dlg.minClusterSize
        
        self.dlg.processSpatialButton.clicked.connect(self.alerting)
        self.dlg.layerSelect.currentIndexChanged.connect(self.setLayer)
        
        
        # show the dialog 
        self.dlg.show()

        self.log("RUNNING")
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        print("now running")
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

