# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoMet
                                 A QGIS plugin
 The GeoMet plugin is a powerful and user-friendly extension for QGIS, designed to seamlessly integrate real-time weather data with your geospatial projects.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-09-17
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Ahmed Abdelkarim
        email                : a.abdelkarim9696@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsFeatureRequest

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .geo_met_dialog import GeoMetDialog
import os.path
import threading

from . import _import_libs
from .services.weather import Weather
from .jobs.update_weather import UpdateWeatherJobManager



class GeoMet:
    """QGIS Plugin Implementation."""

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
            'GeoMet_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoMet')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        
         # Create a QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_layer)
        
        # Start the timer with a 10-second interval (10000 milliseconds)
        self.timer.start(10000)

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
        return QCoreApplication.translate('GeoMet', message)


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

        icon_path = ':/plugins/geo_met/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GeoMet'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True
        
        self.update_weather_job_manager = UpdateWeatherJobManager()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GeoMet'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = GeoMetDialog()
            
            self.get_all_layers()
            self.dlg.getWeatherBtn.clicked.connect(self.update_layer)
            # self.dlg.startJobBtn.clicked.connect(self.update_weather_job_manager.start_continuous_task)
            import threading
            import time

            # Create a function execution timer
            def execute_function_timer():
                print("hey")
                while True:
                    self.update_weather_job_manager.start_background_task  # Call your function
                    time.sleep(10)  # Sleep for 5 seconds

            # Create a thread for the timer
            timer_thread = threading.Thread(target=execute_function_timer)

            # Start the timer thread
            timer_thread.start()

            # You can stop the timer thread by calling timer_thread.stop() or use some other mechanism to control its execution.
            
            

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        
    # GeoMet
    def get_all_layers(self):
        # Clear the ComboBox to ensure it's empty
        self.dlg.layerList.clear()
        
        # Populate the ComboBox with layer names
        for layer in QgsProject.instance().mapLayers().values():
            self.dlg.layerList.addItem(layer.name())
            
        self.dlg.layerList.currentIndexChanged.connect(self.on_layerList_changed)
            
    
    def on_layerList_changed(self, index):
        # Get the current index and item text
        current_index = self.dlg.layerList.currentIndex()
        selected_item_text = self.dlg.layerList.currentText()
        
        self.set_layer_fields(selected_item_text)
        
    def set_layer_fields(self, layer_name):
        # Get the layer by name
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        self.selected_layer = layer

        # Check if the layer exists
        if layer:
            self.dlg.fieldList.clear()
            # Get the fields from the layer
            fields = layer.fields()
           # Get the fields from the layer
            fields = layer.fields()
            # Populate the ComboBox with field names
            for field in fields:
                self.dlg.fieldList.addItem(field.name())
        else:
            print(f"Layer '{layer_name}' not found.")
            
            
    def get_selected_field(self):
        return self.dlg.fieldList.currentText()
    
    def get_selected_layer(self):
        selected_item_text = self.dlg.layerList.currentText()
        layer = QgsProject.instance().mapLayersByName(selected_item_text)[0]
        return layer
    
    def update_layer(self):
        layer = self.selected_layer
        print(layer.name())
        # Check if the layer exists
        if not layer:
            print(f"Layer '{layer}' not found.")
        else:
            # Start an edit session
            layer.startEditing()

            # Create a feature request to retrieve all features
            # request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)

            # Iterate through all features in the layer
            for feature in layer.getFeatures():
                if feature.geometry() != None:
                    lat = feature.geometry().asPoint().y()
                    lon = feature.geometry().asPoint().x()
                    # create weather instance
                    weather = Weather()
                    current_weather = weather.get_current(lat, lon)
                    feature.setAttribute(self.get_selected_field(), current_weather["current"]["temp_c"])
                    feature.setAttribute('latest_up', current_weather["current"]["last_updated"])
                    # Add more attributes as needed

                    # Update the feature in the layer
                    layer.updateFeature(feature)

            # Commit the changes to the layer
            layer.commitChanges()

            # End the edit session
            layer.rollBack()