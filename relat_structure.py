#%%
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import geopandas as gpd
import shapely


df_munc = pd.read_parquet(r"C:\Users\ferna\Downloads\df_municipios.parquet")

path = "Brasil Geo"
geometries = []
for arq in os.listdir(path):
    geometries.append(pd.read_parquet(os.path.join(path, arq), columns=['CD_MUN','geometry']))

geometries = pd.concat(geometries, axis=0)
geometries['CD_MUN'] = geometries['CD_MUN'].astype(int)
geometries['geometry'] = geometries['geometry'].apply(lambda linha: shapely.wkb.loads(linha))

df_munc = gpd.GeoDataFrame(pd.merge(left=df_munc, right=geometries, on='CD_MUN', how='left')).set_geometry('geometry')

#%%

niteroi = df_munc[df_munc['NM_MUN'] == "São Paulo"]
# %%
colors = sns.color_palette("crest")

font_path = "Assets\Fonts\Afacad-Regular.otf"  # Replace with the actual font file path
custom_font = fm.FontProperties(fname=font_path)

with sns.axes_style({'axes.facecolor': '#00000000', 'figure.facecolor': '#00000000',
    'axes.edgecolor': '#00000000', 'xtick.bottom': False, 'xtick.top': False,
    'ytick.left': False, 'ytick.right': False}):

    fig, ax = plt.subplots()
    
    # plt.figure(figsize=(6, 6))
    pie_graf = plt.pie(niteroi[['valor_adc_serv_essenciais_pub', 'valor_adc_agropecuaria',
        'valor_adc_industria', 'valor_adc_servicos']].iloc[0].to_list(),
        labels=['Serviços Públicos', 'Agro', 'Indústria', 'Serviços'], colors=colors,
        autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': '#EAEAEA'})
    
    # for ind, label in enumerate(ax.get_annotations()):
    #     print(label)

    outline_effect = [pe.withStroke(linewidth=3, foreground="#232323")]

    for text in pie_graf[1]+pie_graf[-1]:
        text.set_fontproperties(custom_font)
        text.set_color("#EAEAEA")
        text.set_size(12)
        text.set_path_effects(outline_effect)

    fig.set_figheight(6, forward=True)
    fig.set_figwidth(6, forward=True)

    fig.savefig("setores_econ.png")


#%%

br_bounds = df_munc.geometry.bounds.agg({'minx':min, 'miny':min, 'maxx':max, 'maxy':max})
br_bounds

regioes = df_munc.groupby('NM_REGIAO').agg({'geometry':lambda linha: linha.representative_point()})

#%%
munc_boundaries = niteroi.geometry.iloc[0].bounds
with sns.axes_style({'axes.facecolor': '#00000000', 'figure.facecolor': '#00000000',
    'axes.edgecolor': '#00000000', 'xtick.bottom': False, 'xtick.top': False,
    'ytick.left': False, 'ytick.right': False}):

    fig, ax = plt.subplots()
    
    df_munc.plot(ax=ax, color="#75BB96", alpha=.8)
    niteroi.plot(ax=ax, color="#064335")


    ax.set_xticklabels([])
    ax.set_yticklabels([])

    fig.set_figheight(4, forward=True)
    fig.set_figwidth(6, forward=True)

    fig.savefig("br_map.png")


#%%
class cidade_brasil():
    def __init__(self, city_infos: pd.DataFrame, lat_lon):
        self.df_munc = city_infos
        self.lat_lon = lat_lon

        self.munc_infos()

    def munc_select(self):
        shp_point = shapely.geometry.Point(self.lat_lon[::-1])
        munc_ref = self.df_munc['geometry'].apply(lambda linha: linha.contains(shp_point))  
        if len(self.df_munc[munc_ref]) ==0:
            return "Coordenada não pertence ao Brasil"
        return self.df_munc[munc_ref]
    

    def munc_infos(self):
        infos_df = self.munc_select().iloc[0]
        self.munc_idh = infos_df['IDHM_2010']
        self.munc_idh_rank = self.df_munc['IDHM_2010'].sort_values(
            ascending=False).to_list().index(self.munc_idh)+1

        self.munc_pib = infos_df['pib']
        self.munc_pib_rank = self.df_munc['pib'].sort_values(
            ascending=False).to_list().index(self.munc_pib)+1

        self.munc_populacao = infos_df['POPULAÇÃO_ESTIMADA']
        self.munc_populacao_rank = self.df_munc['POPULAÇÃO_ESTIMADA'].sort_values(
            ascending=False).to_list().index(self.munc_populacao)+1

        self.munc_densidade = infos_df['densidade_demografica']
        self.munc_densidade_rank = self.df_munc['densidade_demografica'].sort_values(
            ascending=False).to_list().index(self.munc_densidade)+1


sp = niteroi.geometry.iloc[0].representative_point().coords[0]
cidade_brasil(df_munc, sp[::-1]).munc_densidade