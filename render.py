"""
	This script will render the "from-mapnik-xml.xml" file with Mapnik
"""
import sys
import mapnik
from mapnik import *
import json
from pprint import pprint
import psycopg2
import xml.etree.ElementTree as ET
import os.path

# set some default values
destination_lat = '7.626357078552247'
destination_lon = '51.955956115068155'
input_dir = './data' # this is where roads.json and landmarks.json are
input_filesuffix = '' # roadsXXX.json / landmarksXXX.json where XXX is the suffix
output_file = './data/map.png' # output file name and location

"""
Read styles from map.xml and add them to programmatically created layers.
This allows us to use dynamically generated file names, unique for each request.
Reading GeoJSON via OGR might cause Segmentation Fault on some OS configurations.
"""
def renderMap(destination_lat, destination_lon, input_dir, output_file, input_filesuffix):
	# write the destination point file only if not already created by NodeJS server	
	destination_point_file_path = '%s/destination%s.geojson'%(input_dir, input_filesuffix)
	if os.path.isfile(destination_point_file_path) == False:
		destination = '{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": { "ref": "destination_pt", "name": "This is your destination" }, "geometry": {"type": "Point", "coordinates": [%s, %s] } } ] }'%(destination_lon,destination_lat)
		with open(destination_point_file_path, 'w+') as f:
			read_data = f.write(destination)

	mapfile = 'map.xml'

	m = Map(1024, 1024)
	load_map(m, mapfile)

	"""
	load data sources
	"""
	# roads
	destination_roads_datasource = Ogr(file='%s/roads_with_type%s.json'%(input_dir, input_filesuffix),layer_by_index=0) #,layer='OGRGeoJSON'
	destination_roads = Layer('destination roads')
	destination_roads.cache_features = True
	destination_roads.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
	destination_roads.datasource = destination_roads_datasource

	# same road set, but just for drawing shadows
	shadow_roads_datasource = Ogr(file='%s/roads_with_type%s.json'%(input_dir, input_filesuffix),layer_by_index=0) #,layer='OGRGeoJSON'
	shadow_roads = Layer('road background')
	shadow_roads.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
	shadow_roads.datasource = shadow_roads_datasource

	# landmarks file (points)
	landmarks_datasource = Ogr(file='%s/landmarks%s.json'%(input_dir, input_filesuffix),layer_by_index=0) #,layer='OGRGeoJSON'
	landmarks = Layer('landmarks')
	landmarks.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
	landmarks.datasource = landmarks_datasource

	# destination point
	destination_datasource = Ogr(file='%s/destination%s.geojson'%(input_dir, input_filesuffix),layer_by_index=0,) #,layer='OGRGeoJSON'
	destination = Layer('destination point')
	destination.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
	destination.datasource = destination_datasource

	# add the styling that we got from map.xml to the map
	style_shadows    = m.find_style('shadows')
	style_autobahn   = m.find_style('autobahn')
	style_shields    = m.find_style('shields')
	style_streets    = m.find_style('streets')
	style_landmarks  = m.find_style('landmarks')

	# apply styles to map & layers, the ordering is important to not get wrong overlap
	m.append_style('shadows',   style_shadows)
	m.append_style('autobahn',  style_autobahn)
	m.append_style('streets',   style_streets)
	m.append_style('landmarks', style_landmarks)
	m.append_style('shields',   style_shields)

	shadow_roads.styles.append('shadows')
	destination_roads.styles.append('autobahn')
	destination_roads.styles.append('streets')
	landmarks.styles.append('landmarks')
	destination.styles.append('landmarks')
	destination_roads.styles.append('shields')

	# finally add layers to the map and render to file
	m.layers.append(shadow_roads)
	m.layers.append(destination_roads)
	m.layers.append(landmarks)
	m.layers.append(destination)

	print m.layers[0].envelope()
	print m.layers[1].envelope()

	m.zoom_to_box(m.layers[1].envelope()) 
	render_to_file(m, output_file) 
	print m.envelope()

"""
Fetch a single road from the database by osm_id
"""
def getAttribute(osm_id):
	cur.execute("SELECT type FROM roads WHERE osm_id=%s", (osm_id,))
	return cur.fetchone()

"""
Add the "type" attribute from another OSM data import in a Postgres database
"""
def addAttribute(dataPart):
	if dataPart.has_key('osm_id'):
		this_type = getAttribute(dataPart['osm_id'])
		if this_type == "":
			this_type = "None"
		dataPart['type'] = '%s' % this_type
	return dataPart

"""
We will add road type from the database in case it is not already provided by the filtering algorithm
"""
def fetchAttributes(input_dir, input_filesuffix):
	with open('%s/roads%s.json'%(input_dir, input_filesuffix)) as data_file: 
		json_with_attr_added = json.load(data_file, object_hook = addAttribute)
		with open('%s/roads_with_type%s.json'%(input_dir, input_filesuffix), 'w') as fp:
			json.dump(json_with_attr_added, fp)

"""
Use the existing mapnik config file for database access
"""
with open('config.xml') as data_file:
	st = data_file.read()
	e = ET.fromstring( "<a>%s</a>"%st )

conn = psycopg2.connect(dbname=e[1].text, port=e[2].text, user=e[3].text, password=e[4].text, host=e[5].text)
cur = conn.cursor()

if len(sys.argv) >= 5:
	destination_lat  = sys.argv[1:][0]
	destination_lon  = sys.argv[1:][1]
	input_dir        = sys.argv[1:][2]
	output_file      = sys.argv[1:][3]
	input_filesuffix = sys.argv[1:][4]
	print sys.argv
	fetchAttributes(input_dir, input_filesuffix)
	renderMap(destination_lat, destination_lon, input_dir, output_file, input_filesuffix)
else:
	print 'Usage: python test.py start_longitude start_latitude inputDirectory outputFilename filesuffix'
	print 'E.g.   python test.py 7.3828125 52.26815737376817 ./data output123.png asdf'
	sys.exit()