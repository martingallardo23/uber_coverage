import subprocess
subprocess.call([r'C:/OSGeo4W/bin/python-qgis.bat'])
import glob
import os
import sys
from qgis.core import (
     QgsApplication, 
     QgsProcessingFeedback, 
     QgsVectorLayer
)

# Set up QGIS environment

QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

sys.path.append('C:/OSGeo4W/apps/qgis/python/plugins')

import processing
from processing.core.Processing import Processing
Processing.initialize()

# Merge all geojson files

files = glob.glob('../../get_polygons/output/*.geojson')

out_dir = '../output/uber_polygons.shp'

parameters = {'CRS': None, 
            'LAYERS': files, 
            'OUTPUT': out_dir}

processing.run('qgis:mergevectorlayers', parameters) 
