import json
import statsmodels.api as sm
import dash_table
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
import numpy as np

df= pd.read_excel('kdn_data.xlsx',header=0)

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
    trace1.append(go.Choroplethmapbox(
        geojson=geo_str,
        locations=df['자치구'].tolist(),
        z=df[Type].tolist(),
        text=suburbs,
        featureidkey="properties.name",
        colorscale=color_deep,
        colorbar=dict(thickness=20, ticklen=3),
        zmin=0,
        zmax=df[Type].max() + 0.7,
        visible=False,
        subplot='mapbox1',
        hovertemplate="<b>%{text}</b><br><br>" +
                      "value: %{z}<br>" +
                      "<extra></extra>"))

trace1[0]['visible'] = True

trace2 = []

for Type in Types:
    trace2.append(go.Bar(
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

trace2[0]['visible'] = True

layout = go.Layout(
    title={'text': '서울특별시 자치구별 전력사용량(인당)',
           'font': {'size': 28,
                    'family': 'Arial'}},
    autosize=True,

    mapbox1=dict(
        domain={'x': [0.3, 1], 'y': [0, 1]},
        center=dict(lat=latitude, lon=longitude),
        style="open-street-map",
        # accesstoken = mapbox_accesstoken,
        zoom=9),

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

""" 선택 위젯 
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
]))"""

fig = go.Figure(data=trace1 + trace2, layout=layout)

df2= pd.read_excel('kdn_data2.xlsx',header=0)
new_df = df2.set_index('자치구')

Sucide_rate = new_df['자살률'].values
old = new_df['독거노인 수'].values
park = new_df['도보생활권공원면적(1인당)'].values
park_size = new_df['공원면적'].values
facility = new_df['노인시설합계'].values

Sucide_rate = Sucide_rate.reshape(-1,1)
old = old.reshape(-1,1)
park = park.reshape(-1,1)
park_size = park_size.reshape(-1,1)
facility = facility.reshape(-1,1)

#회귀 분석
results_old = sm.OLS(old, sm.add_constant(Sucide_rate)).fit()
results_park = sm.OLS(park, sm.add_constant(Sucide_rate)).fit()
results_parksize = sm.OLS(park_size, sm.add_constant(Sucide_rate)).fit()
results_facility = sm.OLS(facility, sm.add_constant(Sucide_rate)).fit()

#회귀모형의 p-value
S_old = results_old.f_pvalue
S_park = results_park.f_pvalue
S_park_size = results_parksize.f_pvalue
S_facility = results_facility.f_pvalue

coe_df = pd.DataFrame({
    'x': ["독거노인 수", "1인당 도보생활권공원면적(㎡)", "공원면적", "노인시설합계"],
    'y': [S_old, S_park, S_park_size, S_facility]
})
#오름차순 정렬
coe_df = coe_df.sort_values(['y'],ascending=True)
#상위 2개 뽑아냄
top2 = coe_df.iloc[:2]

fig2 = px.bar(coe_df, x="x", y="y", title="회귀모형 P-Value")

app=dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div(children=[
        html.H1(children='한전KDN 자살 예방 대시보드',
                style={"fontSize": "48px"},
                className="header-title"
                ),
        html.P(
            children="Analyze the "
                     " Power Consumption & Sucide Rate  in Seoul",
            className="header-description"
        ),

        dcc.Graph(
            id='example-graph-1',
            figure=fig
        ),

        html.Div(children='''
               Data source from https://github.com/dongh3930/dashboard-kdh
           ''')]),
    html.Div([
        html.H1(children='자살률과 변수 데이터들의 회귀분석 결과(P-Value)',
                style={"fontSize": "20px"},
                className="header-title"
                ),
        dcc.Graph(
            id='example-graph-2',
            figure=fig2
        ),
        html.Div(children='''
        유의미한 인과관계를 보이는 Top 2 Data (P-Value < 0.05)
        ''')]),
        html.Div([
            dash_table.DataTable(
                id='datatable_id',
                data = top2.to_dict('record'),
                columns=[{"name": i, "id": i} for i in top2.columns])
            ]),
])


if __name__ =='__main__':
    app.run_server(debug=False)