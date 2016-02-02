import mapnik
from mapnik import *

print mapnik.mapnik_version_string()

m = Map(1024, 1024)
m.background = mapnik.Color('white')
m.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"

ds = Ogr(file='point.geojson', layer='OGRGeoJSON')
pt = Layer('Point')
pt.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
pt.datasource = ds

style1 = mapnik.Style()
rule1 = mapnik.Rule()
rule1.symbols.append(mapnik.LineSymbolizer(mapnik.Color('#00ff00'), 5))
style1.rules.append(rule1)
m.append_style('Points', style1)
pt.styles.append('Points')

m.layers.append(pt)
m.zoom_all()

render_to_file(m, 'point.png') 
print m.envelope()