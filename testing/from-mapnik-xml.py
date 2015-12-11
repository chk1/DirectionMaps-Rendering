"""
	This script will render the "from-mapnik-xml.xml" file with Mapnik
"""
from mapnik import *

mapfile = 'from-mapnik-xml.xml'
map_output = 'from-mapnik-xml.png'

m = Map(1024, 1024)
load_map(m, mapfile)
bbox=(Envelope(836454, 6785976, 858862, 6797391)) # Muenster

m.zoom_to_box(bbox) 
render_to_file(m, map_output) 