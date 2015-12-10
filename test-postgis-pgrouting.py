import mapnik
from mapnik import GeoJSON, PostGIS

### Set up map and style rules

m = mapnik.Map(1440,800)
m.background = mapnik.Color('white')

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
point_symbolizer = mapnik.PointSymbolizer(mapnik.PathExpression("flag3w.png"))
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

dbparams = dict(dbname='directionmaps',table='planet_osm_line',user='postgres',password='postgres')
postgis = PostGIS(**dbparams)
layer1 = mapnik.Layer('streets full')
layer1.datasource = postgis
layer1.styles.append('MyStyle')
m.layers.append(layer1)

#dijkstra_query = SELECT seq, id1 AS node, id2 AS edge, cost FROM pgr_dijkstra('SELECT id, source, target, st_length(geom_way) as cost FROM hh_2po_4pgr', 128, 5103, false, false) 

query = '(SELECT * FROM planet_osm_line WHERE highway IN (\'primary\', \'secondary\', \'motorway\')) as highwaylines'
datasource_line = PostGIS(host='localhost', dbname='directionmaps', user='postgres', password='postgres', table=query, geometry_field='way')
layer2 = mapnik.Layer('tertiary ways')
layer2.datasource = datasource_line
layer2.styles.append('Highlights')
#m.layers.append(layer2)

query2 = """
(SELECT way FROM planet_osm_line
WHERE osm_id IN (

	SELECT osm_id FROM hh_2po_4pgr 
	WHERE id IN (

		SELECT id2 AS node FROM pgr_dijkstra('
			SELECT id AS id,
			 source::integer,
			 target::integer,
			 cost::double precision AS cost
			FROM hh_2po_4pgr',
		128, 5103, false, false) 

	)
)) as dijkstra
"""

datasource_line2 = PostGIS(host='localhost', dbname='directionmaps', user='postgres', password='postgres', table=query2, geometry_field='way', extent_from_subquery=True)
layer3 = mapnik.Layer('test route')
layer3.datasource = datasource_line2
layer3.styles.append('Highlights3')
m.layers.append(layer3)

query3 = '(SELECT * FROM planet_osm_point WHERE osm_id = 3374898279) as destination'
datasource_pt = PostGIS(host='localhost', dbname='directionmaps', user='postgres', password='postgres', table=query3, geometry_field='way')
layer4 = mapnik.Layer('destionation point')
layer4.datasource = datasource_pt
layer4.styles.append('MyDestination')
#m.layers.append(layer4)

#extent = mapnik.Box2d(836454, 6785976, 858862, 6797391)
#m.zoom_to_box(extent)
m.zoom_all()

mapnik.render_to_file(m, 'world.png', 'png')

exit()
