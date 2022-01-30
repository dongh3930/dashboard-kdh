import json
import folium
import matplotlib.pyplot as plt
import dash
from dash import dcc
from dash import html
#import dash_core_components as dcc
#import dash_html_components as html
import plotly.express as px
import pandas as pd

app=dash.Dash(__name__)
server = app.server

df= pd.read_excel('kdn.xls',header=0)
df = df.set_index('자치구')

#서울시 '구'별 경계선을 그리기 위한 json파일 로딩
geo_path = '02. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

#서울시 중심의 위도와 경도, 확대 비율, 지도 모양 설정
map = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='openstreetmap')

fig = map.choropleth(geo_data=geo_str, data = df['인구당전력'],columns=[df.index, df['인구당전력']], fill_color='PuRd', key_on='feature.id')

app.layout = html.Div(children=[
    html.H1(children='서울특별시 자치구별 인구당 전력 사용량'),

    html.Div(children='''
        Dash:A web application framework for your data.
    '''),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ =='__main__':
    app.run_server(debug=False)