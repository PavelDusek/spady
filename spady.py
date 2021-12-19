# coding: utf-8
from shapely.geometry import Point, Polygon, LineString
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import pyproj
import numpy as np
import requests
import re


def wgs84_to_sjtsk( lon, lat ):
    sjtsk = pyproj.Proj("+init=epsg:5514")
    wgs = pyproj.Proj("+init=epsg:4326")
    return pyproj.transform(wgs, sjtsk, lon, lat)
    #lon_, lat_ = pyproj.transform(wgs, sjtsk, lon, lat)
    #return ((-1)*lon_, (-1)*lat_)

def wgs84_to_Point( lon, lat ):
    lon_, lat_ = wgs84_to_sjtsk( lon, lat )
    return Point(lon_, lat_)

def changeName( name ):
    to_change = {
            'Praha-Čakovice': 'Čakovice',
            'Praha-Troja': 'Troja',
            'Nedvězí u Říčan': 'Nedvězí',
            'Újezd u Průhonic': 'Újezd',
            }
    for old, new in to_change.items():
        name = name.replace(old, new)
    return name

# Use file from https://geoportal.cuzk.cz/Default.aspx?mode=TextMeta&side=dsady_RUIAN&metadataID=CZ-CUZK-SH-V&mapid=5&menu=252
geo_df = gpd.read_file('JTSK/SPH_OKRES.shp')
geo_df = geo_df.head(13)

dist = 100_000

# Use file from https://geoportal.cuzk.cz/Default.aspx?mode=TextMeta&side=mapy_data200&metadataID=CZ-CUZK-DATA200-VODSTVO-V&head_tab=sekce-02-gp&menu=2292
reky   = gpd.read_file('HYDRO/WatrcrsL.shp')
berounka = reky.loc[ reky['NAMN1'] == 'Berounka' ].reset_index(drop = True)

lgd_kwds = {
        'title': 'Primární spády\niktových center\nv Praze a Středních\nČechách',
        'loc': 'upper left',
        'bbox_to_anchor': (0.75, 1.00),
        'ncol': 1
        }

mc = gpd.read_file('JTSK/SPH_MC.shp')
mc['praha'] = mc['NAZEV_MC'].apply(lambda x: 'Praha' in x)
praha = mc.loc[ mc['praha'] ]
praha['NAZEV_MC'] = praha['NAZEV_MC'].apply(lambda x: x.replace("Praha-", "") )

query = """SELECT ?okres ?okresLabel ?coordinates ?nemocnice ?population {
  VALUES (?okres ?nemocnice) {
    (wd:Q973974 "VFN")       #Praha 1
    (wd:Q2444636 "VFN")      #Praha 2
    (wd:Q2598899 "FNKV")     #Praha 3

    #(wd:Q2686587 "VFN/FTN") #Praha 4
    (wd:Q2623877 "VFN")      #Praha 4 Michle
    (wd:Q1969345 "VFN")      #Praha 4 Nusle
    (wd:Q2638290 "VFN")      #Praha 4 Podolí
    (wd:Q2499127 "VFN")      #Praha 4 Braník
   
    (wd:Q2834321 "FTN")      #Praha 4 Hodkovičky
    (wd:Q868618 "FTN")       #Praha 4 Krč
    (wd:Q2693443 "FTN")      #Praha 4 Lhotka
    (wd:Q3499406 "FTN")      #Praha 4 Záběhlice
    (wd:Q2661930 "FTN")      #Praha 4 Kunratice
   
    (wd:Q84492217 "FNM")     #Praha 5
    (wd:Q84572475 "FNM")     #Velká Chuchle
    (wd:Q84565071 "FNM")     #Slivenec

    (wd:Q84598568 "ÚVN")     #Praha 6
    (wd:Q3490548  "ÚVN")     #Lysolaje
    (wd:Q2317527  "ÚVN")     #Nebušice
    (wd:Q14544932 "ÚVN")     #Suchdol
    (wd:Q1810336  "ÚVN")     #Přední Kopanina

    (wd:Q84492955 "NNH")     #Praha 7
    (wd:Q2643835  "NNH")     #Troja
   
    #(wd:Q84492981 "VFN/FNM") #Praha 8
    (wd:Q174248  "VFN")      #Praha 8 Kobylisy
    (wd:Q1822800 "VFN")      #Praha 8 Ďáblice
    (wd:Q2003486 "VFN")      #Praha 8 Libeň
    (wd:Q3499350 "VFN")      #Praha 8 Dolní Chabry
    (wd:Q3499380 "VFN")      #Praha 8 Střížkov
    (wd:Q2717469 "VFN")      #Praha 8 Březiněves
    (wd:Q1734030 "FNM")      #Praha 8 Karlín
    (wd:Q2440414 "FNM")      #Praha 8 Čimice
    (wd:Q2442419 "FNM")      #Praha 8 Bohnice
                   
    (wd:Q2750534 "ÚVN")      #Praha 9
    (wd:Q2444921 "FNKV")     #Praha 10

    (wd:Q84497080 "FTN")     #Praha 11
    (wd:Q3563232  "FTN")     #Šeberov
    (wd:Q3563133  "FTN")     #Újezd
    (wd:Q3509048  "FTN")     #Křeslice

    (wd:Q84498882 "FTN")     #Praha 12
    (wd:Q84499835 "FTN")     #Libuš

    (wd:Q84565554 "FNM")     #Praha 13
    (wd:Q84566351 "FNM")     #Řeporyje
    
    (wd:Q84763109 "NNH")     #Praha 14
    (wd:Q3489932  "NNH")     #Dolní Počernice

    (wd:Q84946861 "FNKV")    #Praha 15
    (wd:Q3490214  "FNKV")    #Dolní Měcholupy
    (wd:Q3490530  "FNKV")    #Petrovice
    (wd:Q3563100  "FNKV")    #Štěrboholy
    (wd:Q2061921  "FNKV")    #Dubeč

    (wd:Q84572284 "FNM")     #Praha 16
    (wd:Q3490395  "FNM")     #Lipence
    (wd:Q84572977 "FNM")     #Zbraslav
    (wd:Q2456160  "FNM")     #Lochkov

    (wd:Q3498074 "FNM")      #Praha 17
    (wd:Q84593853 "FNM")      #Zličín

    (wd:Q13361279 "ÚVN")     #Praha 18
    (wd:Q3489907  "ÚVN")     #Čakovice

    (wd:Q84846030 "ÚVN")     #Praha 19
    (wd:Q3563089  "ÚVN")     #Vinoř
    (wd:Q3509354  "ÚVN")     #Satalice

    (wd:Q106070574 "NNH")    #Praha 20

    (wd:Q84846483 "NNH")     #Praha 21
    (wd:Q2501433  "NNH")     #Klánovice
    (wd:Q600063   "NNH")     #Koloděje
    (wd:Q693350   "NNH")     #Běchovice

    (wd:Q84947654 "FNKV")    #Praha 22
    (wd:Q84947682 "FNKV")    #Kolovraty
    (wd:Q3509457  "FNKV")    #Královice
    (wd:Q3509772  "FNKV")    #Nedvězí, Nedvězí u Říčan
    (wd:Q2709316  "FNKV")    #Benice

    (wd:Q302778 "FNM/VFN")   #Praha-zapad
    (wd:Q645376 "NNH/FNKV")  #Praha-vychod
       
    (wd:Q330653 "NNH") #Praha vychod Úvaly
   
    (wd:Q480085  "FNM")  # Beroun
    (wd:Q792883  "FNKV") # Benešov

    (wd:Q837635 "Kladno") #Kladno
    (wd:Q338296 "Kladno") #Kladno
    (wd:Q852463 "Kladno/ Mladá Boleslav") #Mělník
    (wd:Q852468 "Mladá Boleslav") #Mladá Boleslav
    (wd:Q852491 "Kolín") #Nymburk
    (wd:Q847318 "Kolín") #Kolín
    (wd:Q268426 "Kolín") #Kutná Hora
    (wd:Q852457 "Příbram") #Příbram
  }
  ?okres wdt:P625 ?coordinates.
  ?okres wdt:P1082 ?population.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],cs". }
}"""
url = 'https://query.wikidata.org/sparql'
r = requests.get(url, params = {'format': 'json', 'query': query})
wikidata = r.json()
df = pd.json_normalize(wikidata['results']['bindings'])
colnames = ['okres.value', 'nemocnice.value', 'coordinates.value', 'population.value', 'okresLabel.value']
df = df[colnames]
df.rename(columns = { colname:colname.replace(".value", "") for colname in colnames }, inplace = True)
getCoord = re.compile("\((\d+\.\d+) (\d+\.\d+)\)")
df['coord'] = df['coordinates'].apply( lambda c: getCoord.search(c).groups() )
df['lon'] = [ float(coord[0]) for coord in df['coord'] ]
df['lat'] = [ float(coord[1]) for coord in df['coord'] ]
df['NAZEV_MC'] = df['okresLabel'].apply(changeName)
df['okres'] = df['okresLabel'].apply(lambda x: 'okres' in x)

uvaly = df.loc[ df['okresLabel'] == 'Úvaly' ]
uvaly['geometry'] = uvaly[['lon', 'lat']].apply( lambda row: wgs84_to_Point(row['lon'], row['lat'] ), axis=1)
uvaly = gpd.GeoDataFrame(uvaly, geometry = 'geometry')
p0 = uvaly['geometry'].values[0]
uvaly_polygon = Polygon([
    (p0.x-dist, p0.y-0*dist),
    (p0.x+dist, p0.y-0*dist),
    (p0.x+dist, p0.y-1*dist),
    (p0.x-dist, p0.y-1*dist)
    ] )
uvaly_box = gpd.GeoSeries([uvaly_polygon])
praha_vychod = geo_df.loc[ geo_df['NAZEV_LAU1'] == 'Praha-východ'].reset_index(drop = True )
praha_vychod_sever = praha_vychod.copy()
praha_vychod_sever['geometry'] = praha_vychod.difference(uvaly_box)
praha_vychod_sever['NAZEV_LAU1'] = 'Praha-východ (sever)'
praha_vychod_sever['nemocnice'] = 'NNH'
praha_vychod_jih   = praha_vychod.copy()
praha_vychod_jih['geometry'] = praha_vychod.intersection(uvaly_box)
praha_vychod_jih['NAZEV_LAU1'] = 'Praha-východ (jih)'
praha_vychod_jih['nemocnice'] = 'FNKV'

praha_zapad = geo_df.loc[ geo_df['NAZEV_LAU1'] == 'Praha-západ'].reset_index(drop = True )
berounka_intersect = gpd.sjoin( berounka, praha_zapad, op='intersects').reset_index(drop = True )
berounka_x, berounka_y = [], []
for i in [ 7, 8, 4, 5, 6, 2, 1, 0, 3 ]:
    berounka_x.extend( berounka_intersect.loc[i, 'geometry'].xy[0] ) 
    berounka_y.extend( berounka_intersect.loc[i, 'geometry'].xy[1] ) 
berounka_x.extend( [ berounka_x[-1] + dist, berounka_x[-1] + dist, berounka_x[0]       , berounka_x[0] - dist ] )
berounka_y.extend( [ berounka_y[-1] + dist, berounka_y[-1] - dist, berounka_y[0] - dist, berounka_y[0]        ] )
berounka_xy = list( zip( berounka_x, berounka_y ) )
berounka_box = Polygon( berounka_xy )
praha_zapad_sever = praha_zapad.copy()
praha_zapad_sever['geometry'] = praha_zapad.difference(berounka_box)
praha_zapad_sever['NAZEV_LAU1'] = 'Praha-západ (sever)'
praha_zapad_sever['nemocnice'] = 'FNM'
praha_zapad_jih   = praha_zapad.copy()
praha_zapad_jih['geometry'] = praha_zapad.intersection(berounka_box)
praha_zapad_jih['NAZEV_LAU1'] = 'Praha-západ (jih)'
praha_zapad_jih['nemocnice'] = 'VFN'

okresy = df.loc[ df['okres'] ]
okresy['NAZEV_LAU1'] = okresy['okresLabel'].apply(lambda x: x.replace("okres ", "") )
okresym = geo_df.merge(okresy, on='NAZEV_LAU1')
okresym = pd.concat( [
    okresym.loc[ (okresym['NAZEV_LAU1'] != 'Praha-východ') & (okresym['NAZEV_LAU1'] != 'Praha-západ') ],
    praha_vychod_sever,
    praha_vychod_jih,
    praha_zapad_sever,
    praha_zapad_jih,
    ])
praham = praha.merge(df, on='NAZEV_MC', how='left')

ax = okresym.plot(column = 'nemocnice', legend = True, legend_kwds = lgd_kwds )
praham.plot(ax = ax, column = 'nemocnice', legend = True, legend_kwds = lgd_kwds )
plt.savefig('spady.png')
plt.show()
