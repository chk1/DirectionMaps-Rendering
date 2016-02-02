"""
	This script will combine several PostGIS layers into a map and save it as a PNG file

	Layer 1: All lines in the database table planet_osm_line
	Layer 2: Highways from the same table
	Layer 3: Two lines filtered by osm_id from the same table
	Layer 4: A point symbolized by a finish line flag

"""

import mapnik
from mapnik import GeoJSON, PostGIS

### Set up map and style rules

m = mapnik.Map(1440,800)
m.background = mapnik.Color('black')

s = mapnik.Style()
s2 = mapnik.Style()
s3 = mapnik.Style()
s4 = mapnik.Style()
r = mapnik.Rule()
r2 = mapnik.Rule()
r3 = mapnik.Rule()
r4 = mapnik.Rule()

line_symbolizer = mapnik.LineSymbolizer(mapnik.Color('#777777'), 1)
line_symbolizer2 = mapnik.LineSymbolizer(mapnik.Color('#bbbb77'), 2)
line_symbolizer3 = mapnik.LineSymbolizer(mapnik.Color('#00ff00'), 5)
point_symbolizer = mapnik.PointSymbolizer(mapnik.PathExpression("assets/flag3w.png"))
r.symbols.append(line_symbolizer)
r2.symbols.append(line_symbolizer2)
r3.symbols.append(line_symbolizer3)
r4.symbols.append(point_symbolizer)

s.rules.append(r)
s2.rules.append(r2)
s3.rules.append(r3)
s4.rules.append(r4)
m.append_style('MyStyle',s)
m.append_style('Highlights',s2)
m.append_style('Highlights3',s3)
m.append_style('MyDestination',s4)

### Set up map layers

dbparams = dict(dbname='directionmaps',table='planet_osm_line',user='postgres',password='postgres')
postgis = PostGIS(**dbparams)
layer1 = mapnik.Layer('streets full')
layer1.datasource = postgis
layer1.styles.append('MyStyle')
m.layers.append(layer1)

query = '(SELECT * FROM planet_osm_line WHERE highway in (\'primary\', \'secondary\', \'motorway\')) as highwaylines'
datasource_line = PostGIS(host='localhost', dbname='directionmaps', user='postgres', password='postgres', table=query, geometry_field='way')
layer2 = mapnik.Layer('tertiary ways')
layer2.datasource = datasource_line
layer2.styles.append('Highlights')
m.layers.append(layer2)

query2 = '(SELECT * FROM planet_osm_line WHERE osm_id IN (200143872, -4238144)) as routinglines'
datasource_line2 = PostGIS(host='localhost', dbname='directionmaps', user='postgres', password='postgres', table=query2, geometry_field='way')
layer3 = mapnik.Layer('test route')
layer3.datasource = datasource_line2
layer3.styles.append('Highlights3')
m.layers.append(layer3)

query3 = '(SELECT * FROM planet_osm_point WHERE osm_id = 3374898279) as destination'
datasource_pt = PostGIS(host='localhost', dbname='directionmaps', user='postgres', password='postgres', table=query3, geometry_field='way')
layer4 = mapnik.Layer('destionation point')
layer4.datasource = datasource_pt
layer4.styles.append('MyDestination')
m.layers.append(layer4)

# zoom to Muenster
extent = mapnik.Box2d(836454, 6785976, 858862, 6797391)
m.zoom_to_box(extent)
#m.zoom_all()

mapnik.render_to_file(m, 'from-postgis.png', 'png') # save the image
mapnik.save_map(m, "huehu.xml")

exit()
