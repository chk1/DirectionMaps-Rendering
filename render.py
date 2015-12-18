"""
	This script will render the "from-mapnik-xml.xml" file with Mapnik
"""
from mapnik import *

mapfile = 'map.xml'
map_output = 'data/out.png'

m = Map(1024, 1024)
load_map(m, mapfile)
print m.layers[0].envelope()
print m.layers[1].envelope()
#bbox=(Envelope(836454, 6785976, 858862, 6797391)) # Muenster

m.zoom_to_box(m.layers[0].envelope()) 
render_to_file(m, map_output) 
print m.envelope()