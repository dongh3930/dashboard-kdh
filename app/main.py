import dash
from dash import dcc
from dash import html
#import dash_core_components as dcc
#import dash_html_components as html
import plotly.express as px
import pandas as pd

app=dash.Dash(__name__)
server = app.server

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig=px.bar(df,x="Fruit",y="Amount",color="City",barmode="group")

app.layout = html.Div(children=[
    html.H1(children='1인당 전력사용량과 자살율의 상관관계'),

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