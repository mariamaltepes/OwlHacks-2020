import os
from datetime import date
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
np.warnings.filterwarnings('ignore')
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import plotly.graph_objs as go

scope = ['https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive']

basedir = os.path.abspath(os.path.dirname(__file__))
data_json = basedir+'/amazing-insight.json'

creds = ServiceAccountCredentials.from_json_keyfile_name(data_json, scope)
connection = gspread.authorize(creds)

worksheet = connection.open("Owlhacks").sheet1
dv = get_as_dataframe(worksheet)
dv = dv.loc[:, ~dv.columns.str.contains('^Unnamed')]

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
                meta_tags=[
                    {
                        'name' : 'image',
                        'property' : 'og:image',
                        'content' : 'assets/thumbnail.PNG'
                    }
])
server = app.server
app.config.suppress_callback_exceptions = True
app.title = "Philadelphia Database"

if 'DYNO' in os.environ:
    app_name = os.environ['DASH_APP_NAME']
else:
    app_name = 'dash-3dscatterplot'

today = date.today()
today = today.strftime("%m/%d/%Y")

ageRange = []
for age in dv["age"]:
    if age <= 20:
        age = int(age)
        ageRange.append("18-20")
    elif age > 20 and age <= 30:
        age = int(age)
        ageRange.append("21-30")
    elif age > 30 and age <= 40:
        age = int(age)
        ageRange.append("31-40")
    elif age > 40 and age <= 50:
        age = int(age)
        ageRange.append("41-50")
    elif age > 50:
        age = int(age)
        ageRange.append("50+")
    else:
        ageRange.append("None")    
dv["age"] = ageRange

timeRange = []
for time in dv['prelim_hearing_time']:
    if time >= 0 and time < 5:
        time = int(time)
        timeRange.append("0-4")
    elif time >= 5 and time < 10:
        time = int(time)
        timeRange.append("5-9")
    elif time >= 10 and time < 15:
        time = int(time)
        timeRange.append("10-14")
    elif time >= 15 and time < 20:
        time = int(time)
        timeRange.append("15-19")
    elif time >= 20 and time <= 24:
        time = int(time)
        timeRange.append("20-24")
    else:
        timeRange.append("None")
dv['prelim_hearing_time'] = timeRange

dv.dropna(
    axis=0,
    how='all',
    thresh=None,
    subset=None,
    inplace=True
)
dv.fillna("None", inplace=True)

officerCount = {}

for officer in dv["arresting_officer"]:
    if officer not in officerCount:
        officerCount[officer] = 1
    else:
        officerCount[officer] += 1

dv['arrests'] = "any" 
off = list(dict.fromkeys(dv['arresting_officer']))
for i in off:
    dv.loc[dv.arresting_officer == i, 'arrests'] = officerCount[i]

dv['Color'] = "any" 
names = list(dict.fromkeys(dv['bail_type']))
color = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#bcbd22',  # curry yellow-green
    '#17becf',  # blue-teal
    'black', 'blue', 'blueviolet', 'cadetblue',
    'chartreuse', 'chocolate', 'coral', 'cornflowerblue',
    'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
    'darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen',
    'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
    'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
    'darkslateblue', 'darkslategray', 'darkslategrey',
    'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
    'dimgray', 'dimgrey', 'dodgerblue', 'firebrick',
    'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro',
    'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green',
    'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo',
    'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
    'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
    'lightgoldenrodyellow', 'lightgray', 'lightgrey',
    'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen',
    'lightskyblue', 'lightslategray', 'lightslategrey',
    'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
    'linen', 'magenta', 'maroon', 'mediumaquamarine',
    'mediumblue', 'mediumorchid', 'mediumpurple',
    'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
    'mediumturquoise', 'mediumvioletred', 'midnightblue',
    'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy',
    'oldlace', 'olive', 'olivedrab', 'orange', 'orangered',
    'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
    'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink',
    'plum', 'powderblue', 'purple', 'red', 'rosybrown',
    'royalblue', 'saddlebrown', 'salmon', 'sandybrown',
    'seagreen', 'seashell', 'sienna', 'silver', 'skyblue',
    'slateblue', 'slategray', 'slategrey', 'springgreen',
    'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise',
    'violet', 'wheat', 'whitesmoke', 'yellow',
    'yellowgreen'
]
color_index = 0
for i in names:
    dv.loc[dv.bail_type == i, 'Color'] = color[color_index]
    color_index += 1
#print(dv[dv.bail_type == "Monetary"]) #check for colors you do not like

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
])

zipsCounter = {}

for zips in dv.zip:
    if zips not in zipsCounter:
        zipsCounter[zips] = 1
    else:
        zipsCounter[zips] += 1

Graph_Height = 610

dv['docket_no'] = dv['docket_no'].astype(str)
dv['age'] = dv['age'].astype(str)
dv['offenses'] = dv['offenses'].astype(str)
dv['case_status'] = dv['case_status'].astype(str)
dv['arresting_officer'] = dv['arresting_officer'].astype(str)
dv['arrests'] = dv['arrests'].astype(str)
dv['docket_no'] = dv['docket_no'].astype(str)
dv['attorney'] = dv['attorney'].astype(str)
dv['bail_set_by'] = dv['bail_set_by'].astype(str)

home = dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([html.H1("Graph 2")],style={'text-align':"center", "margin-left":"auto","margin-right":"auto", 'color':"white"}),

                html.Div(dcc.Dropdown(id="select-xaxis2", placeholder = "Select x-axis", value = "arrest_date",
                options=[{'label': i.title(), 'value': i}  for i in dv.columns[10:15]], clearable=False),
                style={"margin-left": "auto", "margin-right": "auto", "width": "80%"}),

                html.Div(dcc.Dropdown(id="select-yaxis2", placeholder = "Select y-axis", value = "arrests",
                options=[{'label': i.title(), 'value': i} for i in dv.columns[15:-1]], clearable=False),
                style={"margin-left": "auto", "margin-right": "auto", "width": "80%"}),

                html.Div(dcc.Dropdown(id="select-zaxis2", placeholder = "Select z-axis", value = "zip",
                options=[{'label': i.title(), 'value': i} for i in dv.columns[10:-1]], clearable=False),
                style={"margin-left": "auto", "margin-right": "auto", "width": "80%"})
            ],id="compare_dropdown"),

            html.Div([html.H1("Philly Database")],
                style={'text-align':"center", "margin-right":"auto","margin-left":"auto", 'color':"white","width": "80%","padding-top":"10%"}),

            html.Div([
                html.Div(dcc.Dropdown(id="select-xaxis", placeholder = "Select x-axis", value = "arrest_date",
                options=[{'label': i.title(), 'value': i}  for i in dv.columns[10:15]], clearable=False),
                style={"margin-left": "auto", "margin-right": "auto", "width": "80%"}),

                html.Div(dcc.Dropdown(id="select-yaxis", placeholder = "Select y-axis", value = "arrests",
                options=[{'label': i.title(), 'value': i} for i in dv.columns[15:-1]], clearable=False),
                style={"margin-left": "auto", "margin-right": "auto", "width": "80%"}),

                html.Div(dcc.Dropdown(id="select-zaxis", placeholder = "Select z-axis", value = "zip",
                options=[{'label': i.title(), 'value': i} for i in dv.columns[10:-1]], clearable=False),
                style={"margin-left": "auto", "margin-right": "auto", "width": "80%"}),

                html.Div([
                    dbc.Row([
                        dcc.RadioItems(
                            id='toggle',
                            options=[{'label': i, 'value': i} for i in ['Show Less','Show More']],
                            value='Show Less',
                            labelStyle={"padding-right":"10px","margin":"auto"},
                            style={"text-align":"center","margin":"auto"}
                        ),
                    ],style={'text-align':"center","margin-left": "auto", "margin-right": "auto"}),
                    
                    html.Div(id='controls-container', children=[
                                            
                        html.Hr(),
                                                    
                        html.Div(
                            dcc.RadioItems(
                                id='addComp',
                                options=[{'label': i, 'value': i} for i in ['No Compare','Compare']],
                                value='No Compare',
                                labelStyle={"padding-right":"10px","margin":"auto"}
                            )
                        ,style={"margin":"auto"}),

                    html.Hr(),
                                            
                    html.Details([
                        html.Summary("Docket Number"),
                        dcc.Checklist(
                            id = 'gasses',
                            options= [{'label': number, 'value': number} for number in sorted(list(dict.fromkeys(dv['docket_no'])))],
                            value = list(dict.fromkeys(dv['docket_no'])),
                            labelStyle={'display': 'block'}
                        ),
                   ]),

                    html.Hr(),

                    html.Details([
                        html.Summary("Status"),
                        dcc.Checklist(
                            id = 'surfactants',
                            options= [{'label': status, 'value': status} for status in list(dict.fromkeys(dv['case_status']))],
                            value = list(dict.fromkeys(dv['case_status'])),
                            labelStyle={'display': 'block'}
                        ),
                    ]),

                    html.Hr(),

                    html.Details([
                        html.Summary("Arresting Officer"),
                        dcc.Checklist(
                            id = 'sconc',
                            options= [{'label': off, 'value': off} for off in sorted(list(dict.fromkeys(dv['arresting_officer'])))],
                            value = list(dict.fromkeys(dv['arresting_officer'])),
                            labelStyle={'display': 'block'}
                        ),
                    ]),

                    html.Hr(),

                    html.Details([
                        html.Summary("Attorney"),
                        dcc.Checklist(
                            id = 'additives',
                            options= [{'label': ad, 'value': ad} for ad in sorted(list(dict.fromkeys(dv['attorney'])))],
                            value = list(dict.fromkeys(dv['attorney'])),
                            labelStyle={'display': 'block'}
                        ),
                    ]),

                    html.Hr(),

                    html.Details([
                        html.Summary("Age Range"),
                        dcc.Checklist(
                            id = 'aconc',
                            options= [{'label': age, 'value': age} for age in sorted(list(dict.fromkeys(dv['age'])))],
                            value = list(dict.fromkeys(dv['age'])),
                            labelStyle={'display': 'block'}
                        ),
                    ]),

                    html.Hr(),

                    html.Details([
                        html.Summary("Bail Set By"),
                        dcc.Checklist(
                            id = 'lp',
                            options= [{'label': bail, 'value': bail} for bail in sorted(list(dict.fromkeys(dv['bail_set_by'])))],
                            value = list(dict.fromkeys(dv['bail_set_by'])),
                            labelStyle={'display': 'block'}
                        ),
                    ]),
                                            
                    html.Hr(),

                    html.Details([
                        html.Summary("Prelimary Hearing Time"),
                        dcc.Checklist(
                            id = 'pht',
                            options= [{'label': hear, 'value': hear} for hear in sorted((list(dict.fromkeys(dv['prelim_hearing_time']))))],
                            value = list(dict.fromkeys(dv['prelim_hearing_time'])),
                            labelStyle={'display': 'block'}
                        ),
                    ]),
                                            
                    html.Hr(),

                    ],style={"display":"none"}),
                ],style={"text-align":"center", "margin-left": "auto", "margin-right": "auto", "width": "80%", "backgroundColor": 'white', "border-radius":3,"position":"relative"}),

            ],style={'text-align':"center","margin-left": "auto", "margin-right": "auto", "width": "100%"}),

            dcc.Link('About', href='/about',style={'position':'absolute','top':0, 'left':0,"padding":5,"color":"white","font-size":18}),
        ],style={'backgroundColor': '#9E1B34'},width=2),

        dbc.Col([
                dcc.Tabs(id="tabs", children=[
                    dcc.Tab(label='3-Dimensions', children=[
                        dbc.Row([                            
                            dbc.Col([
                                    dcc.Graph(id="comp1_3D_graph",
                                    config = {'toImageButtonOptions':
                                    {'width': None,
                                    'height': None,
                                    'format': 'png',
                                    'filename': '3D_Plot_Comp1'}
                                    })
                            ]),

                            dbc.Col([
                                    dcc.Graph(id="comp2_3D_graph",
                                    config = {'toImageButtonOptions':
                                    {'width': None,
                                    'height': None,
                                    'format': 'png',
                                    'filename': '3D_Plot_Comp2'}
                                    })
                            ],id="compare_graph")
                        ],no_gutters=True),

                        dbc.Row([
                            dbc.Col(
                                dt.DataTable(
                                    id='comp1_3D_table',
                                    page_current=0,
                                    page_size=75,
                                    export_format='xlsx',
                                    style_data_conditional=[
                                    {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                    }],
                                    style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                                    style_table={'max-height': "20vh", "height": "20vh"},
                                    fixed_rows={'headers': True},
                                ),
                            style={"padding-left":20,"padding-right":20}),

                            dbc.Col(
                                dt.DataTable(
                                    id='comp2_3D_table',
                                    page_current=0,
                                    page_size=75,
                                    columns=[{'id': c, 'name': c} for c in dv.columns[10:-1]],
                                    export_format='xlsx',
                                    style_data_conditional=[
                                    {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                    }],
                                    style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                                    style_table={'max-height': "20vh", "height": "20vh"},
                                    fixed_rows={'headers': True},
                                )
                            ,style={"padding-left":20,"padding-right":20},id="compare_table")
                        ],no_gutters=True)
                    ]),

                    dcc.Tab(label='2-Dimensions', children=[
                        dbc.Row([
                            dbc.Col(
                                html.Div([
                                    dcc.Graph(id="comp1_2D_graph",
                                    config = {'toImageButtonOptions':
                                    {'width': None,
                                    'height': None,
                                    'format': 'png',
                                    'filename': '2D_Plot_Comp1'}
                                    })
                                ])
                            ),

                            dbc.Col(
                                html.Div([
                                    dcc.Graph(id="comp2_2D_graph",
                                        config = {'toImageButtonOptions':
                                        {'width': None,
                                        'height': None,
                                        'format': 'png',
                                        'filename': '2D_Plot_Comp2'}
                                        })
                                    ])
                            ,id="compare_graph_2D")
                        ],no_gutters=True),

                        dbc.Row([
                            dbc.Col(
                                dt.DataTable(
                                    id='comp1_2D_table',
                                    page_current=0,
                                    page_size=75,
                                    export_format='xlsx',
                                    style_data_conditional=[
                                    {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                    ],
                                    style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                                    style_table={"height":"20vh","min-height":"20vh"},
                                    fixed_rows={'headers': True},
                                ),style={"padding-left":20,"padding-right":20}
                            ),

                            dbc.Col(
                                dt.DataTable(
                                    id='comp2_2D_table',
                                    page_current=0,
                                    page_size=75,
                                    columns=[{'id': c, 'name': c} for c in dv.columns[10:-1]],
                                    export_format='xlsx',
                                    style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                                    ],
                                    style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                                    style_table={"height":"20vh","min-height":"20vh"},
                                    fixed_rows={'headers': True},
                                )
                            ,style={"padding-left":20,"padding-right":20},id="compare_table_2D")
                        ],no_gutters=True)  
                    ]),

                    dcc.Tab(label='Table', children=[
                        dt.DataTable(
                            id='table',
                            page_current=0,
                            page_size=75,
                            style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                            }],
                            style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                            style_table={'height': "87vh",'min-height': "87vh"},
                            fixed_rows={'headers': True}
                        )
                    ])
                ])
        ])
    ],no_gutters=True,style={"height":"100vh"})

about = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.Link('Home', href='/',style={'position':'absolute','top':0, 'left':0,"padding":5,"color":"white","font-size":18}),
            width=3
        ),
        dbc.Col([
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='About Us', children=[
                    html.Br(),
                    html.H1("Team",style={"text-align":"center"}),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardImg(src="/assets/Voytek.jpg", top=True,style={"height":"25vh","width":"100%"}),
                                dbc.CardBody(
                                    [
                                        html.H5("Josh Voytek", className="card-title"),
                                        html.Hr(),
                                        html.H6("Mechanical Engineering Student"),
                                        html.A("josh.voytek@temple.edu", href="mailto: josh.voytek@temple.edu"),
                                        html.A("LinkedIn Profile", href="https://www.linkedin.com/in/josh-voytek/",
                                        style={"display":"block"},target="_blank")
                                    ]
                                ,style={"text-align":"center"})
                            ])
                        ),
                            
                        dbc.Col(
                            dbc.Card([
                                dbc.CardImg(src="/assets/Maltepes.JPG", top=True,style={"height":"25vh","width":"100%"}),
                                dbc.CardBody(
                                    [
                                        html.H5("Maria Maltepes", className="card-title"),
                                        html.Hr(),
                                        html.H6("Bioinformatics Student"),
                                        html.A("maria.maltepes@temple.edu", href="mailto: maria.maltepes@temple.edu"),
                                        html.A("LinkedIn Profile", href="https://www.linkedin.com/in/maria-m-07a884109/",
                                        style={"display":"block"},target="_blank")
                                    ]
                                ,style={"text-align":"center"})
                            ])
                        ),
                    ],style={"margin-left":"auto","margin-right":"auto","width":"60%"},no_gutters=True),
                    html.Br(),
                    html.P("Currently juniors planning on a future in software development or analytics."
                    ,style={"font-size":23,"padding-left":30,"padding-right":30,"text-align":"center"})         
                ]),
                dcc.Tab(label='About The Project', children=[
                    html.Br(),
                    html.H1("Project",style={"text-align":"center"}),
                    html.Br(),
                    html.Div([

                        html.P("Firstly, we would like to say thank you to Owlhacks and the Philly Bail Project for giving us the opportunity to create something meaningful.",
                        style={"font-size":23,"padding-left":30,"padding-right":30}),

                        html.P("The purpose of this project was to create a data visualization tool that makes the analysis of large data easier. " +
                           "The tool takes in data, and utilizes an array of sorting algorithms both manually implemented and included in vanilla Plotly. " +
                           "The tool was repurposed from an existing research project of Josh's, which analyzed multivariate Surfactant Literature, specifically for applications in " +
                           "waterless geothermal fracking. When we reviewed the Philadelphia Bail Project's data, we figured this tool would be perfect to provide a meaningful analysis. " +
                           "Our hope is that this project will be used as a method of understanding the way our criminal justice system works in Philadelphia. " + 
                           "Meaningful connections can be drawn from unlikely places, and a tool like this can be used to catalyze such connections.",
                            style={"font-size":23,"padding-left":50,"padding-right":50}
                        )

                    ],style={"text-align":"center"}),
                    html.P("Last Updated: " + today,style={"text-align":"center"})
                ]),
            ]),
        ],style={"backgroundColor":"white"}),
        dbc.Col(style={'backgroundColor': '#9E1B34',"height":"100vh"},width=3)
    ],style={'backgroundColor': '#9E1B34',"height":"100%"},no_gutters=True)
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/about':
        return about
    else:
        return home

@app.callback(
    Output('controls-container', 'style'),
    [Input('toggle', 'value')])

def toggle_container(toggle_value):
    if toggle_value == 'Show More':
        return {'display': 'block','max-height':600,'overflow-y':'auto',"border-top":"1px black solid"}
    else:
        return {'display': 'none'}

@app.callback(
    [Output('compare_dropdown', 'style'),
     Output('compare_graph', 'style'),
     Output('compare_table', 'style'),
     Output('compare_graph_2D', 'style'),
     Output('compare_table_2D', 'style')],
    [Input('addComp', 'value')])

def toggle_compare_container(compare_value):
    if compare_value == 'Compare':
        return [{'display': 'block',"position":"absolute","top":"50%","margin-right":"auto","margin-left":"auto","width":"100%","text-align":"center"},
                {'display': 'block'},
                {'display': 'block'},
                {'display': 'block'},
                {'display': 'block'}]
    else:
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]

@app.callback(
    [Output("table", "data"),
     Output("table", "columns")],
    [Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_table(ga, sur, surc, add, addc, lp, pht):
    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    return (
        cleaned.to_dict('records'), [{'id': c, 'name': c} for c in cleaned.columns[:]],
    )

@app.callback(
    Output('table', 'style_data_conditional'),
    [Input("select-xaxis", "value"),
     Input("select-yaxis", "value"),
     Input("select-zaxis", "value")]
)
def update_styles(x,y,z):
    return [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgb(248, 248, 248)'
    },
    {
        'if': { 'column_id': x },
        'background_color': '#0066CC',
        'color': 'white',
    },
    {
        'if': { 'column_id': y },
        'background_color': '#0066CC',
        'color': 'white',
    },
    {
        'if': { 'column_id': z },
        'background_color': '#0066CC',
        'color': 'white',
    }]

@app.callback(
    Output("comp1_2D_graph", "figure"),
    [Input("select-xaxis", "value"),
     Input("select-yaxis", "value"),
     Input('addComp', 'value'),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp1_2D_graph(selected_x, selected_y, comp, ga, sur, surc, add, addc, lp, pht):
    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    data = []
    legend_orientation = {}

    for i in names:
        name_array = cleaned[cleaned.bail_type == i]
        
        trace = go.Scattergl(x=name_array[selected_x],y=name_array[selected_y], 
            hovertext= "Docket Number: " + name_array.docket_no
            + "<br />Case Status: " + name_array.case_status
            + "<br />Offenses: " + name_array.offenses
            + "<br />Arresting Officer: " + name_array.arresting_officer + " (arrests: " + dv["arrests"] + ")"
            + "<br />Attorney: " + name_array.attorney
            + "<br />Age: " + name_array["age"] 
            + "<br />Bail Set By: " + name_array.bail_set_by 
            + "<br />Preliminary Hearing Time: " + name_array.prelim_hearing_time,
            hoverinfo='text',mode='markers', marker={'size': 10, 'opacity': 0.8, 'color' : name_array.Color},
            name=i)

        data.append(trace)

    if(comp == "No Compare"):
        legend_orientation={
                "font_size": 24,
        }

    if(comp == "Compare"):
        legend_orientation={
                "orientation":"h",
                "xanchor":"center",
                "x":0.5,
                "yanchor":"bottom",
                "y":1,
                "font_size": 20,
        }

    if selected_x == "zip":
        typecat = "category"
    else:
        typecat = "-"

    return {
        'data': data,
        'layout': go.Layout(
            yaxis={
                "title":selected_y,
                "titlefont_size":20,
                "tickfont_size":18,
            },
            xaxis={
                "type":typecat,
                "title":selected_x,
                "titlefont_size":20,
                "tickfont_size":18
            },
            legend=legend_orientation,
            font={
                "family":"Times New Roman",
            },
            hovermode="closest",
            height=Graph_Height
        )
    }

@app.callback(
    [Output("comp1_2D_table", "data"),
     Output("comp1_2D_table", "columns")],
    [Input("select-xaxis", "value"),
     Input("select-yaxis", "value"),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp1_2D_table(selected_x, selected_y, ga, sur, surc, add, addc, lp, pht):
    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    final = cleaned.columns
    final = final.drop([selected_x,selected_y])
    cleaned = cleaned.drop(final, axis=1)

    return (
        cleaned.to_dict('records'), [{'id': c, 'name': c} for c in cleaned.columns]
    )

@app.callback(
    Output("comp2_2D_graph", "figure"),
    [Input("select-xaxis2", "value"),
     Input("select-yaxis2", "value"),
     Input('addComp', 'value'),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp2_2D_graph(selected_x, selected_y, comp, ga, sur, surc, add, addc, lp, pht):
    if comp == "No Compare":
        return "none"

    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    data = []

    for i in names:
        name_array = cleaned[cleaned.bail_type == i]

        trace = go.Scattergl(x=name_array[selected_x],y=name_array[selected_y], 
            hovertext= "Docket Number: " + name_array.docket_no
            + "<br />Case Status: " + name_array.case_status
            + "<br />Offenses: " + name_array.offenses
            + "<br />Arresting Officer: " + name_array.arresting_officer + " (arrests: " + dv["arrests"] + ")"
            + "<br />Attorney: " + name_array.attorney
            + "<br />Age: " + name_array["age"] 
            + "<br />Bail Set By: " + name_array.bail_set_by 
            + "<br />Preliminary Hearing Time: " + name_array.prelim_hearing_time,
            hoverinfo='text',mode='markers', marker={'size': 10, 'opacity': 0.8, 'color' : name_array.Color},
            name=i)

        data.append(trace)
    if selected_x == "zip":
        typecat = "category"
    else:
        typecat = "-"
        
    return {
        'data': data,
        'layout': go.Layout(
            yaxis={
                "title":selected_y,
                "titlefont_size":20,
                "tickfont_size":18,
            },
            xaxis={
                "type":typecat,
                "title":selected_x,
                "titlefont_size":20,
                "tickfont_size":18
            },
            legend={
                "orientation":"h",
                "xanchor":"center",
                "x":0.5,
                "yanchor":"bottom",
                "y":1,
                "valign":"middle",
                "font_size": 20,
            },
            font={
                "family":"Times New Roman",
            },
            hovermode="closest",
            height=Graph_Height
        )
    }

@app.callback(
    [Output("comp2_2D_table", "data"),
     Output("comp2_2D_table", "columns")],
    [Input("select-xaxis", "value"),
     Input("select-yaxis", "value"),
     Input("addComp","value"),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp2_2D_table(selected_x, selected_y, comp, ga, sur, surc, add, addc, lp, pht):
    if comp == "No Compare":
        return "none"

    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    final = cleaned.columns
    final = final.drop([selected_x,selected_y])
    cleaned = cleaned.drop(final, axis=1)

    return (
        cleaned.to_dict('records'), [{'id': c, 'name': c} for c in cleaned.columns]
    )

@app.callback(
    Output("comp1_3D_graph", "figure"),
    [Input("select-xaxis", "value"),
     Input("select-yaxis", "value"),
     Input("select-zaxis", "value"),
     Input('addComp', 'value'),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp1_3D_graph(selected_x, selected_y, selected_z, comp, ga, sur, surc, add, addc, lp, pht):
    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    data = []

    for i in names:
        name_array = cleaned[cleaned.bail_type == i]
        
        trace = go.Scatter3d(x = name_array[selected_x], y = name_array[selected_y], z = name_array[selected_z], 
            hovertext= "Docket Number: " + name_array.docket_no
            + "<br />Case Status: " + name_array.case_status
            + "<br />Offenses: " + name_array.offenses
            + "<br />Arresting Officer: " + name_array.arresting_officer + " (arrests: " + dv["arrests"] + ")"
            + "<br />Attorney: " + name_array.attorney
            + "<br />Age: " + name_array["age"] 
            + "<br />Bail Set By: " + name_array.bail_set_by 
            + "<br />Preliminary Hearing Time: " + name_array.prelim_hearing_time,
            hoverinfo='text',mode='markers', marker={'size': 10, 'opacity': 0.8, 'color' : name_array.Color},
            name=i)

        data.append(trace)
        
    if(comp == "No Compare"):
        legend_orientation={
                "font_size": 24,
        }

    if(comp == "Compare"):
        legend_orientation={
                "orientation":"h",
                "xanchor":"center",
                "x":0.5,
                "yanchor":"bottom",
                "y":1,
                "valign":"middle",
                "font_size": 20,
        }
    if selected_x == "zip":
        typecat = "category"
    else:
        typecat = "-"

    return {"data": data,
            "layout": go.Layout(
                hovermode="closest",
                legend=legend_orientation,
                xaxis={
                    "type":typecat
                },
                font={
                    "size": 16,
                    "family": "Times New Roman",
                },
                scene={
                    "camera":{"center":dict(x=0.05,y=0,z=-0.25)},
                    "xaxis": {"title": f"{selected_x.title()}"},
                    "yaxis": {"title": f"{selected_y.title()}"},
                    "zaxis": {"title": f"{selected_z.title()}"}
                },
                margin={
                    "b":0,
                    "l":0,
                    "r":0
                },
                height=Graph_Height
            )}

@app.callback(
    [Output("comp1_3D_table", "data"),
     Output("comp1_3D_table", "columns")],
    [Input("select-xaxis", "value"),
     Input("select-yaxis", "value"),
     Input("select-zaxis", "value"),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp1_3D_table(selected_x, selected_y,selected_z, ga, sur, surc, add, addc, lp, pht):
    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    final = cleaned.columns
    final = final.drop([selected_x,selected_y,selected_z])
    cleaned = cleaned.drop(final, axis=1)

    return (
        cleaned.to_dict('records'), [{'id': c, 'name': c} for c in cleaned.columns]
    )

@app.callback(
    Output("comp2_3D_graph", "figure"),
    [Input("select-xaxis2", "value"),
     Input("select-yaxis2", "value"),
     Input("select-zaxis2", "value"),
     Input("addComp","value"),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp2_3D_graph(selected_x, selected_y, selected_z, comp, ga, sur, surc, add, addc, lp, pht):
    if comp == "No Compare":
        return "none"

    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    data = []

    for i in names:      
        name_array = cleaned[cleaned.bail_type == i]  
        trace = go.Scatter3d(x = name_array[selected_x], y = name_array[selected_y], z = name_array[selected_z], 
            hovertext= "Docket Number: " + name_array.docket_no
            + "<br />Case Status: " + name_array.case_status
            + "<br />Offenses: " + name_array.offenses
            + "<br />Arresting Officer: " + name_array.arresting_officer + " (arrests: " + dv["arrests"] + ")"
            + "<br />Attorney: " + name_array.attorney
            + "<br />Age: " + name_array["age"] 
            + "<br />Bail Set By: " + name_array.bail_set_by 
            + "<br />Preliminary Hearing Time: " + name_array.prelim_hearing_time,
            hoverinfo='text',mode='markers', marker={'size': 10, 'opacity': 0.8, 'color' : name_array.Color},
            name=i)

        data.append(trace)
    
    if selected_x == "zip":
        typecat = "category"
    else:
        typecat = "-"

    return {"data": data,
            "layout": go.Layout(
                hovermode="closest",
                legend={
                    "orientation":"h",
                    "xanchor":"center",
                    "x":0.5,
                    "yanchor":"bottom",
                    "y":1,
                    "valign":"middle",
                    "font_size": 20,
                },
                xaxis={
                    "type":typecat
                },
                font={
                    "size": 16,
                    "family": "Times New Roman",
                },
                scene={
                    "camera":{"center":dict(x=0.05,y=0,z=-0.25)},
                    "xaxis": {"title": f"{selected_x.title()}"},
                    "yaxis": {"title": f"{selected_y.title()}"},
                    "zaxis": {"title": f"{selected_z.title()}"}
                },
                margin={
                    "b":0,
                    "l":0,
                    "r":0
                },
                height=Graph_Height
            )}

@app.callback( #updates 2d graph relative to selected axes and checklist data
    [Output("comp2_3D_table", "data"),
     Output("comp2_3D_table", "columns")],
    [Input("select-xaxis2", "value"),
     Input("select-yaxis2", "value"),
     Input("select-zaxis2", "value"),
     Input("addComp","value"),
     Input('gasses', 'value'),
     Input('surfactants', 'value'),
     Input('sconc', 'value'),
     Input('additives', 'value'),
     Input('aconc', 'value'),
     Input('lp', 'value'),
     Input('pht', 'value')],
)
def update_comp2_3D_table(selected_x, selected_y,selected_z, comp, ga, sur, surc, add, addc, lp, pht):
    if comp == "No Compare":
        return "none"

    cl = dv[dv['docket_no'].isin(ga)]
    ea = cl[cl['case_status'].isin(sur)]
    n = ea[ea["arresting_officer"].isin(surc)]
    e = n[n['attorney'].isin(add)]
    d = e[e['age'].isin(addc)]
    f = d[d['bail_set_by'].isin(lp)]
    cleaned = f[f['prelim_hearing_time'].isin(pht)]

    final = cleaned.columns
    final = final.drop([selected_x,selected_y,selected_z])
    cleaned = cleaned.drop(final, axis=1)

    return (
        cleaned.to_dict('records'), [{'id': c, 'name': c} for c in cleaned.columns]
    )

if __name__ == '__main__':
    app.run_server(debug=True)