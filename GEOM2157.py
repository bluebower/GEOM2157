# GEOM2157 Geospatial Programming by G. Tong, 2019

# Import statements
from qgis.core import QgsVectorLayer
import qgis.utils
import os
import processing

# Remove all map layers
QgsProject.instance().removeAllMapLayers()

# Data input
filepath = "/Users/gary/Downloads/GP/"
gccsaLayer = filepath + "GCCSA2016" + ".shp"
suburbsLayer = filepath + "Suburbs" + ".shp"
crashLayer = filepath + "Crash5Y" + ".csv"
shopsLayer = filepath + "Shops" + ".shp"

# Data output
gccsaLayer1 = filepath + "GCCSA2016_MEL" + ".shp"
gccsaLayer2 = filepath + "GCCSA2016_MEL1" + ".shp"
suburbsLayer1 = filepath + "Suburbs_MEL" + ".shp"
crashLayer1 = filepath + "Crash5Y" + ".shp"
crashLayer2 = filepath + "Crash5Y1" + ".shp"
crashLayer3 = filepath + "Crash5Y_MEL" + ".shp"
shopsLayer1 = filepath + "Shops1" + ".shp"
shopsLayer2 = filepath + "Shops_MEL" + ".shp"
shopsBufLayer1 = filepath + "Shops_MEL_buffer" + ".shp"
shopsBufLayer2 = filepath + "Shops_MEL_bufferDis" + ".shp"
shopsCrashLayer1 = filepath + "ShopsCrash1" + ".shp"
shopsCrashLayer2 = filepath + "ShopsCrash2" + ".shp"
shopsCrashLayer3 = filepath + "ShopsCrash3" + ".shp"
shopsCrashLayer4 = filepath + "ShopsCrash4" + ".shp"

# Extract the Greater Melbourne region from GCCSA2016
parameterDict = {'FIELD': 'GCCSA_NAME',
                 'INPUT': gccsaLayer,
                 'OPERATOR': 0,
                 'OUTPUT': gccsaLayer1,
                 'VALUE': 'Greater Melbourne'
                 }
extractByAttribute = processing.run(
    'qgis:extractbyattribute', parameterDict)

# Reproject Greater Melbourne to EPSG:28355 - GDA94 / MGA zone 55 - Projected
parameterDict = {'INPUT': gccsaLayer1,
                 'OUTPUT': gccsaLayer2,
                 'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:28355')
                 }
assignProjection = processing.run('native:reprojectlayer', parameterDict)
print('Loaded: Greater Melbourne boundary.')
layer = iface.addVectorLayer(gccsaLayer2, '', 'ogr')

# Hide Greater Melbourne region output from GCCSA2016
QgsProject.instance().layerTreeRoot().findLayer(
    layer.id()).setItemVisibilityChecked(False)

# Reproject Suburbs data to EPSG:28355 - GDA94 / MGA zone 55 - Projected
parameterDict = {'INPUT': suburbsLayer,
                 'OUTPUT': suburbsLayer1,
                 'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:28355')
                 }
assignProjection = processing.run('native:reprojectlayer', parameterDict)

# Extract suburbs from the Greater Melbourne region for site context
parameterDict = {'INPUT': suburbsLayer,
                 'INTERSECT': gccsaLayer2,
                 'OUTPUT': suburbsLayer1,
                 'PREDICATE': [0]
                 }
extractByLocation = processing.run(
    'native:extractbylocation', parameterDict)
print("Loaded: Suburbs.")
layer = iface.addVectorLayer(suburbsLayer1, '', 'ogr')

# Load crash data from .csv to .shp
parameterDict = {'INPUT': crashLayer,
                 'MFIELD': None,
                 'OUTPUT': crashLayer1,
                 'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
                 'XFIELD': 'LONGITUDE',
                 'YFIELD': 'LATITUDE',
                 'ZFIELD': None,
                 }
createShapefile = processing.run(
    'qgis:createpointslayerfromtable', parameterDict)

# Reproject crash data to EPSG:28355 - GDA94 / MGA zone 55 - Projected
parameterDict = {'INPUT': crashLayer1,
                 'OUTPUT': crashLayer2,
                 'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:28355')
                 }
assignProjection = processing.run('native:reprojectlayer', parameterDict)

# Extract crash data from Greater Melbourne region
parameterDict = {'INPUT': crashLayer2,
                 'INTERSECT': gccsaLayer2,
                 'OUTPUT': crashLayer3,
                 'PREDICATE': [6]}
extractByLocation = processing.run('qgis:extractbylocation', parameterDict)
print('Loaded: Crash data.')
layer = iface.addVectorLayer(crashLayer3, '', 'ogr')

# Reproject shopping centre location data to EPSG:28355 - GDA94 / MGA zone 55 - Projected
parameterDict = {'INPUT': shopsLayer,
                 'OUTPUT': shopsLayer1,
                 'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:28355')
                 }
assignProjection = processing.run('native:reprojectlayer', parameterDict)

# Extract shopping centre location data from Greater Melbourne region
parameterDict = {'INPUT': shopsLayer1,
                 'INTERSECT': gccsaLayer2,
                 'OUTPUT': shopsLayer2,
                 'PREDICATE': [6]}
extractByLocation = processing.run('qgis:extractbylocation', parameterDict)
print('Loaded: Shopping centre locations.')
layer = iface.addVectorLayer(shopsLayer2, '', 'ogr')

# Buffer shopping centre locations by 1km radial distance (non-dissolve)
parameterDict = {'INPUT': shopsLayer2,
                 'DISTANCE': 1000,
                 'SEGMENTS': 5,
                 'END_CAP_STYLE': 0,
                 'JOIN_STYLE': 0,
                 'MITER_LIMIT': 10,
                 'DISSOLVE': False,
                 'OUTPUT': shopsBufLayer1,
                 }
buffer = processing.run('native:buffer', parameterDict)
print('Loaded: Shopping centre location 1km buffers')
layer = iface.addVectorLayer(shopsBufLayer1, '', 'ogr')

# Join crashes to non-dissolved shopping centre buffers using join attributes by location
parameterDict = {'DISCARD_NONMATCHING': False,
                 'INPUT': shopsBufLayer1,
                 'JOIN': crashLayer3,
                 'JOIN_FIELDS': [],
                 'METHOD': 0,
                 'OUTPUT': shopsCrashLayer1,
                 'PREDICATE': [0],
                 'PREFIX': ['']
                 }
joinAttributesByLocation = processing.run(
    'qgis:joinattributesbylocation', parameterDict)

# Hide output shopsCrashLayer1
layer = iface.addVectorLayer(shopsCrashLayer1, '', 'ogr')
QgsProject.instance().layerTreeRoot().findLayer(
    layer.id()).setItemVisibilityChecked(False)

# Summarise crash data for each shopping centre location
parameterDict = {'INPUT_DATASOURCES': [shopsCrashLayer1],
                 'INPUT_GEOMETRY_CRS': QgsCoordinateReferenceSystem('EPSG:28355'),
                 'INPUT_GEOMETRY_FIELD': '',
                 'INPUT_GEOMETRY_TYPE': None,
                 'INPUT_QUERY': 'SELECT *, SUM(ALCOHOL_Y) AS S_ALCOHOL_Y, SUM(ALCOHOL_N) AS S_ALCOHOL_N, SUM(MON) AS S_MON, SUM(TUE) AS S_TUE, SUM(WED) AS S_WED, SUM(THU) AS S_THU, SUM(FRI) AS S_FRI, SUM(SAT) AS S_SAT, SUM(SUN) AS S_SUN, SUM(KMH30) AS S_KMH30, SUM(KMH40) AS S_kmh40, SUM(KMH50) AS S_kmh50, SUM(kmhOTHER) AS S_kmhOTHER, SUM(NODENONINT) AS S_NODENONINT, SUM(NODEINTERS) AS S_NODEINTERS, SUM(NODEOFFROA) AS S_NODEOFFROA, SUM(TOTAL_PERS) AS S_TOTAL_PERS, SUM(INJ_OR_FAT) AS S_INJ_OR_FAT, SUM(FATALITY) AS S_FATALITY, SUM(MALES) AS S_MALES, SUM(FEMALES) AS S_FEMALES, SUM(BICYCLIST) AS S_BICYCLIST, SUM(PASSENGER) AS S_PASSENGER, SUM(DRIVER) AS S_DRIVER, SUM(PEDESTRIAN) AS S_PEDESTRIAN, SUM(PILLION) AS S_PILLION, SUM(MOTORIST) AS S_MOTORIST, SUM(UNKNOWN) AS S_UNKNOWN, SUM(PED_CYCLIS) AS S_PED_CYCLIS, SUM(PED_CYCL_1) AS S_PED_CYCL_1, SUM(OLD_PEDEST) AS S_OLD_PEDEST, SUM(OLD_DRIVER) AS S_OLD_DRIVER, SUM(YOUNG_DRIV) AS S_YOUNG_DRIV, SUM(UNLICENCSE) AS S_UNLICENCSE, SUM(NO_OF_VEHI) AS S_NO_OF_VEHI, SUM(HEAVYVEHIC) AS S_HEAVYVEHIC, SUM(PASSENGERV) AS S_PASSENGERV, SUM(MOTORCYCLE) S_MOTORCYCLE, SUM(PUBLICVEHI) AS S_PUBLICVEHI \nFROM ShopsCrash1\nGROUP BY Centre_ID\n',
                 'INPUT_UID_FIELD': '',
                 'OUTPUT': shopsCrashLayer2
                 }
executeSQL = processing.run('qgis:executesql', parameterDict)

# Drop non-sum fields for each shopping centre location
parameterDict = {'COLUMN':
                 ['X', 'Y', 'ACCIDENT_N', 'ACCIDENT_D', 'ACCIDENT_T', 'ALCOHOL_Y', 'ALCOHOL_N', 'ACCIDENT_1', 'AT1', 'AT2', 'AT3', 'AT4', 'AT5', 'AT6', 'AT7', 'AT8', 'AT9', 'Day', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'HIT_RUN_FL', 'LIGHT_COND', 'SEVERITY', 'kmh30', 'kmh40', 'kmh50', 'kmhOther', 'NODE_ID', 'LONGITUDE', 'LATITUDE', 'nodeNonInt', 'nodeInters', 'nodeOffRoa', 'LGA_NAME', 'VICGRID_X', 'VICGRID_Y', 'TOTAL_PERS', 'INJ_OR_FAT', 'FATALITY', 'SERIOUSINJ', 'OTHERINJUR', 'NONINJURED', 'MALES', 'FEMALES', 'BICYCLIST', 'PASSENGER', 'DRIVER', 'PEDESTRIAN', 'PILLION', 'MOTORIST', 'UNKNOWN', 'PED_CYCLIS', 'PED_CYCL_1', 'OLD_PEDEST', 'OLD_DRIVER', 'YOUNG_DRIV', 'UNLICENCSE', 'NO_OF_VEHI', 'HEAVYVEHIC', 'PASSENGERV', 'MOTORCYCLE', 'PUBLICVEHI', 'RMA'], 'INPUT': shopsCrashLayer2, 'OUTPUT': shopsCrashLayer3
                 }
deleteColumn = processing.run('qgis:deletecolumn', parameterDict)

# Load final output
print("Loaded: Final output ('ShopsCrash3.shp')")
layer = iface.addVectorLayer(shopsCrashLayer3, '', 'ogr')


# Count number of crashes by dissolving shopping centre buffers and joining
# attributes by location. This is to avoid duplicate crash data where crash data may overlap
# more than one shopping centre.
parameterDict = {'FIELD': [],
                 'INPUT': shopsBufLayer1,
                 'OUTPUT': shopsBufLayer2
                 }
dissolve = processing.run('native:dissolve', parameterDict)

parameterDict = {'DISCARD_NONMATCHING': False,
                 'INPUT': shopsBufLayer2,
                 'JOIN': crashLayer3,
                 'JOIN_FIELDS': [],
                 'METHOD': 0,
                 'OUTPUT': shopsCrashLayer4,
                 'PREDICATE': [0],
                 'PREFIX': ['']
                 }
joinAttributesByLocation = processing.run(
    'qgis:joinattributesbylocation', parameterDict)

# Load crash count
print("Loaded: Crash count ('ShopsCrash4.shp')")
layer = iface.addVectorLayer(shopsCrashLayer4, '', 'ogr')
