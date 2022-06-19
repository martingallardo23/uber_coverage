import subprocess
subprocess.call([r'C:/OSGeo4W/bin/python-qgis.bat'])
import glob
import os
import sys
from qgis.core import (
     QgsApplication, 
)
import zipfile

# Set up QGIS environment

QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

sys.path.append('C:/OSGeo4W/apps/qgis/python/plugins')

import processing
from processing.core.Processing import Processing
Processing.initialize()

# Unzip zip_dir to files_dir

files_dir = "../../get_polygons/output"
zip_dir = os.path.join(files_dir, "geojson_files.zip")

with zipfile.ZipFile(zip_dir, 'r') as zip_ref:
    zip_ref.extractall(files_dir)

# Get list of geojson files

files = glob.glob(os.path.join(files_dir, '*.geojson'))

out_dir = '../output/uber_polygons.shp'

# Merge geojson files into one shapefile

parameters = {'CRS': None, 
            'LAYERS': files, 
            'OUTPUT': out_dir}

processing.run('qgis:mergevectorlayers', parameters) 

#Delete all geojson files 
for file in files:
    os.remove(file)
