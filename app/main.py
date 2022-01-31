import json
import folium
import matplotlib.pyplot as plt
import dash
from dash import dcc
from dash import html
#import dash_core_components as dcc
#import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

df= pd.read_excel('kdn.xlsx',header=0)

#서울시 '구'별 경계선을 그리기 위한 json파일 로딩
geo_path = '02. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

Types = ['인구당전력', '자살율(10만명당)', '독거노인 수', '1인당 도보생활권공원면적']

suburbs = df['자치구'].str.title().tolist()

color_deep = [[0.0, 'rgb(253, 253, 204)'],
              [0.1, 'rgb(201, 235, 177)'],
              [0.2, 'rgb(145, 216, 163)'],
              [0.3, 'rgb(102, 194, 163)'],
              [0.4, 'rgb(81, 168, 162)'],
              [0.5, 'rgb(72, 141, 157)'],
              [0.6, 'rgb(64, 117, 152)'],
              [0.7, 'rgb(61, 90, 146)'],
              [0.8, 'rgb(65, 64, 123)'],
              [0.9, 'rgb(55, 44, 80)'],
              [1.0, 'rgb(39, 26, 44)']]

latitude = 37.5502
longitude = 126.982

trace1 = []

for Type in Types:
    trace1.append(go.Bar(
        x=df.sort_values([Type], ascending=True).head(5)[Type],
        y=df.sort_values([Type], ascending=True).head(5)['자치구'].str.title().tolist(),
        xaxis='x2',
        yaxis='y2',
        marker=dict(
            color='rgba(91, 207, 135, 0.3)',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.5),
        ),
        visible=False,
        name='Top 5 gu with the lowest {} value'.format(Type),
        orientation='h',
    ))

trace1[0]['visible'] = True

trace2 = []

for Type in Types:
    trace2.append(go.Choroplethmapbox(
        geojson=geo_str,
        locations=[latitude, longitude],
        z=df[Type].tolist(),
        text=suburbs,
        featureidkey='properties.id',
        colorscale=color_deep,
        colorbar=dict(thickness=20, ticklen=3),
        zmin=0,
        zmax=df[Type].max() + 0.5,
        visible=False,
        subplot='mapbox1',
        hovertemplate="<b>%{text}</b><br><br>" +
                      "value: %{z}<br>" +
                      "<extra></extra>"))

trace2[0]['visible'] = True

layout = go.Layout(
    title={'text': '서울특별시 자치구별 데이터 분포 / Local extinction in 2020',
           'font': {'size': 28,
                    'family': 'Arial'}},
    autosize=True,

    mapbox1=dict(
        domain={'x': [0.3, 1], 'y': [0, 1]},
        center=dict(lat=latitude, lon=longitude),
        style="open-street-map",
        # accesstoken = mapbox_accesstoken,
        zoom=11),

    xaxis2={
        'zeroline': False,
        "showline": False,
        "showticklabels": True,
        'showgrid': True,
        'domain': [0, 0.25],
        'side': 'left',
        'anchor': 'x2',
    },
    yaxis2={
        'domain': [0.4, 0.9],
        'anchor': 'y2',
        'autorange': 'reversed',
    },
    margin=dict(l=100, r=20, t=70, b=70),
    paper_bgcolor='rgb(204, 204, 204)',
    plot_bgcolor='rgb(204, 204, 204)',
)

layout.update(updatemenus=list([
    dict(x=0,
         y=1,
         xanchor='left',
         yanchor='middle',
         buttons=list([
             dict(
                 args=['visible', [True, False, False, False]],
                 label='type: 인구당전력',
                 method='restyle'
             ),
             dict(
                 args=['visible', [False, True, False, False]],
                 label='type: 자살율(10만명당)',
                 method='restyle'
             ),
             dict(
                 args=['visible', [False, False, True, False]],
                 label='type: 독거노인 수',
                 method='restyle'
             ),
             dict(
                 args=['visible', [False, False, False, True]],
                 label='type: 1인당 도보생활권공원면적',
                 method='restyle'
             )
         ]),)
]))

fig = go.Figure(data=trace2 + trace1, layout=layout)

app=dash.Dash(__name__)
server = app.server

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