"""
Loads a GeoJSON and adds additional attributes to it from another database
"""

import json
from pprint import pprint
import psycopg2
import xml.etree.ElementTree as ET

# Fetch data from a database
def getAttribute(osm_id):
	cur.execute("SELECT type FROM roads WHERE osm_id=%s", (osm_id,))
	return cur.fetchone()

# Add the "type" attribute from another OSM data import in a Postgres database
def addAttribute(dataPart):
	if dataPart.has_key('osm_id'):
		dataPart['type'] = '%s' % getAttribute(dataPart['osm_id'])
	return dataPart

# read the XML database config
with open('config.xml') as data_file:
	st = data_file.read()
	e = ET.fromstring( "<a>%s</a>"%st )

conn = psycopg2.connect(dbname=e[1].text, port=e[2].text, user=e[3].text, password=e[4].text, host=e[5].text)
cur = conn.cursor()

with open('data/geojson.json') as data_file: 
	json_with_attr_added = json.load(data_file, object_hook = addAttribute)
	#print json_with_attr_added
	with open('data/result.geojson', 'w') as fp:
		json.dump(json_with_attr_added, fp)
	#print json.dumps(json_with_attr_added)
