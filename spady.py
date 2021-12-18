# coding: utf-8
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np
import requests

# Use file from https://geoportal.cuzk.cz/Default.aspx?mode=TextMeta&side=dsady_RUIAN&metadataID=CZ-CUZK-SH-V&mapid=5&menu=252
geo_df = gpd.read_file('JTSK/SPH_OKRES.shp')
geo_df = geo_df.head(13)

lgd_kwds = {
        'title': 'Primární spády iktových center v Praze a Středních Čechách',
        'loc': 'upper left',
        'bbox_to_anchor': (1, 1.03),
        'ncol': 2
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

    (wd:Q2686587 "VFN/FNM") #Praha 4
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
    (wd:Q84598568 "ÚVN")     #Praha 6
    (wd:Q84492955 "NNH")     #Praha 7
   
    (wd:Q84492981 "VFN/FNM") #Praha 8
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
    (wd:Q84498882 "FTN")     #Praha 12
    (wd:Q84565554 "FNM")     #Praha 13
    (wd:Q84763109 "NNH")     #Praha 14
    (wd:Q84946861 "FNKV")    #Praha 15
    (wd:Q84572284 "FNM")     #Praha 16
    (wd:Q3498074 "FNM")      #Praha 17
    (wd:Q13361279 "ÚVN")     #Praha 18
    (wd:Q84846030 "ÚVN")     #Praha 19
    (wd:Q106070574 "NNH")    #Praha 20
    (wd:Q84846483 "NNH")     #Praha 21
    (wd:Q84947654 "FNKV")    #Praha 22

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
df['NAZEV_MC'] = df['okresLabel']
df['okres'] = df['okresLabel'].apply(lambda x: 'okres' in x)

okresy = df.loc[ df['okres'] ]
okresy['NAZEV_LAU1'] = okresy['okresLabel'].apply(lambda x: x.replace("okres ", "") )
okresym = geo_df.merge(okresy, on='NAZEV_LAU1')
praham = praha.merge(df, on='NAZEV_MC', how='left')

ax = okresym.plot(column = 'nemocnice', legend = True, legend_kwds = lgd_kwds )
praham.plot(ax = ax, column = 'nemocnice')
plt.show()

