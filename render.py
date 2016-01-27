"""
	This script will render the "from-mapnik-xml.xml" file with Mapnik
"""
from mapnik import *

# first command line arguemnt specifies output directory
# second command line arguemnt specifies xml location
dir = '.'
xmldir = '.'
#if sys.argv[1:][0] != None:
#	dir = sys.argv[1:][0]
#if sys.argv[1:][1] != None:
#	xmldir = sys.argv[1:][1]

mapfile = '%s/map.xml'%xmldir
map_output = '%s/data/out.png'%dir

m = Map(1024, 1024)
load_map(m, mapfile)
print m.layers[0].envelope()
print m.layers[1].envelope()
#bbox=(Envelope(836454, 6785976, 858862, 6797391)) # Muenster

m.zoom_to_box(m.layers[0].envelope()) 
render_to_file(m, map_output) 
print m.envelope()
#print m.envelope().maxx

