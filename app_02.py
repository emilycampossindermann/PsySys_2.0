import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
app.title = "PsySys"

# Initialize factors
factors = ["Loss of interest", "Feeling down", "Stress", "Worry", "Overthinking", "Sleep problems", 
           "Joint pain", "Changes is appetite", "Self-blame", "Trouble concentrating", "Procrastinating", 
           "Breakup", "Problems at work", "Interpersonal problems"]

# Function: Embed YouTube video 
def create_iframe(src):
    return html.Iframe(
        width="615",
        height="346",
        src=src,
        allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture;fullscreen"
    )

# Function: Create dropdown menu 
def create_dropdown(id, options, placeholder, multi=True):
    return dcc.Dropdown(id=id, options=options, multi=multi, 
                        value=[], placeholder=placeholder,
                        style={'width': '81.5%'})

# Layout elements
nav_col = dbc.Col(
    [
        html.Br(),
        html.H2("PsySys"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("PsySys Session", href="/psysys-session", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    md=2,
)

content_col = dbc.Col(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ],
    md=10,
)

app.layout = dbc.Container([
    dbc.Row([nav_col, content_col]),
    dcc.Store(id='current-step', data={'step': 0}, storage_type='local')
])

# Define style to initiate components
hidden_style = {'display': 'none'}
visible_style = {'display': 'block'}

# Define content for Home
home_page = html.Div([
    html.H1("Welcome to PsySys App!"),
    html.P("This is the Home tab. More content to come!"),
])

# Stylesheet for network 
stylesheet = [{'selector': 'node','style': {'background-color': 'blue', 'label': 'data(label)'}},
              {'selector': 'edge','style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
    ]

# PsySys step components
step0_content = html.Div([
    html.Br(), html.Br(), html.Br(),
    create_iframe("https://www.youtube.com/embed/d8ZZyuESXcU?si=CYvKNlf17wnzt4iG"),
    html.Br(), html.Br(),
    html.P("Please watch this video and begin with the PsySys session.")
])

step1_content = html.Div([
    html.Br(), html.Br(), html.Br(),
    create_iframe("https://www.youtube.com/embed/ttLzT4U2F2I?si=xv1ETjdc1uGROZTo"),
    html.Br(), html.Br(),
    html.P("Please watch the video. Below choose the factors you are currently dealing with."),
    create_dropdown(id="factor-dropdown", 
                    options=[{'label': factor, 'value': factor} for factor in factors],
                    placeholder='Select factors'),
    html.Br(),
])

step2_content = html.Div([
    html.Br(), html.Br(), html.Br(),
    create_iframe("https://www.youtube.com/embed/stqJRtjIPrI?si=1MI5daW_ldY3aQz3"),
    html.Br(), html.Br(),
    html.P("Please watch the video. Below indicate two causal relations you recognize."),
    html.P("Example: If you feel that normally worrying causes you to become less concentrated, select these factors below in this order.", style={'width': '70%', 'font-style': 'italic', 'color': 'grey'}),
    create_dropdown(id='step2-dropdown1', options=[], placeholder='Select two factors'),
    html.Br(),
    create_dropdown(id='step2-dropdown2', options=[], placeholder='Select two factors'),
    html.Br()
])

step3_content = html.Div([
    html.Br(), html.Br(), html.Br(),
    create_iframe('https://www.youtube.com/embed/EdwiSp3BdKk?si=TcqeWxAlGl-_NUfx'),
    html.Br(), html.Br(),
    html.P("Please watch the video. Below indicate your vicious cycles. You can choose one containing two factors and another one containing three.", style={'width': '70%'}),
    create_dropdown(id='step3-dropdown1', options=[], placeholder='Select two factors that reinforce each other'),
    html.Br(),
    create_dropdown(id='step3-dropdown2', options=[], placeholder='Select three factors that reinforce each other'),
    html.Br()
])

step4_content = html.Div([
    html.Br(), html.Br(), html.Br(),
    create_iframe('https://www.youtube.com/embed/hwisVnJ0y88?si=OpCWAMaDwTThocO6'),
    html.Br(), html.Br(),
    html.P("Please watch the video. Below indicate the factor you feel is the most influential one in your mental-health map.", style={'width': '70%'}),
    create_dropdown(id='step4-dropdown', options=[], placeholder='Select one factor'),
    html.Br()
])

step5_content = html.Div([
    html.Br(), html.Br(), html.Br(),
    cyto.Cytoscape(
        id='graph-output', 
        elements=[],
        layout={'name': 'cose', 'fit': True, 'padding': 10},
        zoom=1,
        pan={'x': 200, 'y': 200},
        stylesheet=stylesheet,
        style={'width': '70%', 'height': '500px'}
    ),
    html.Br()
])

# Define content for PsySys pages
psysys_session_page = html.Div([
    html.Div(id='psysys-content', children=[
        html.Div(step0_content, id='step0-content', style=hidden_style),
        html.Div(step1_content, id='step1-content', style=hidden_style),
        html.Div(step2_content, id='step2-content', style=hidden_style),
        html.Div(step3_content, id='step3-content', style=hidden_style),
        html.Div(step4_content, id='step4-content', style=hidden_style),
        html.Div(step5_content, id='step5-content', style=hidden_style),
        dbc.Button("Back", id='back-button', n_clicks=0, style=hidden_style),
        dbc.Button("Next", id='next-button', n_clicks=0)
    ])
])

# Callback: Define PsySys step visibility
@app.callback(
    [Output('step0-content', 'style'),
     Output('step1-content', 'style'),
     Output('step2-content', 'style'),
     Output('step3-content', 'style'),
     Output('step4-content', 'style'),
     Output('step5-content', 'style'),
     Output('current-step', 'data')],
    [Input('next-button', 'n_clicks'),
     Input('back-button', 'n_clicks')],
    [State('current-step', 'data')]
)
def update_step_visibility(next_clicks, back_clicks, current_step_data):
    # Ensure clicks are not None
    next_clicks = next_clicks or 0
    back_clicks = back_clicks or 0

    # Determine if it's a forward or backward navigation
    if dash.callback_context.triggered[0]['prop_id'] == 'next-button.n_clicks':
        current_step_data['step'] += 1
    elif dash.callback_context.triggered[0]['prop_id'] == 'back-button.n_clicks':
        current_step_data['step'] -= 1
        current_step_data['step'] = max(current_step_data['step'], 0)  # Ensure it's not negative
    
    step = current_step_data['step']
    
    styles = [hidden_style] * 6
    if step < 6:
        styles[step] = visible_style
    else:
        styles[0] = visible_style
        current_step_data['step'] = 0

    return styles + [current_step_data]

@app.callback(
    [Output('next-button', 'children'),
    Output('back-button', 'style')],
    [Input('current-step', 'data')]
)
def update_next_button_label(step_data):
    current_step = step_data['step']
    if current_step == 0:
        return "Start", hidden_style
    elif current_step == 5:
        return "Redo", {'margin-right': '495px'}
    else:
        return "Next", {'margin-right': '495px'}

# Callback: Update Dropdowns
@app.callback(
    [Output('step2-dropdown1', 'options'),
     Output('step2-dropdown2', 'options'),
     Output('step3-dropdown1', 'options'),
     Output('step3-dropdown2', 'options'),
     Output('step4-dropdown', 'options')],
    [Input('factor-dropdown', 'value')]
)
def update_step2_dropdown_options(selected_factors):
    all_options = [{'label': factor, 'value': factor} for factor in selected_factors]
    return all_options, all_options, all_options, all_options, all_options

# Callback: Switch between pages
# @app.callback(
#     Output('page-content', 'children'),
#     [Input('url', 'pathname')]
# )
# def display_page(pathname):
#     if pathname == '/psysys-session':
#         return psysys_session_page
#     else:
#         return home_page

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    [State('current-step', 'data')]
)
def display_page(pathname, current_step_data):
    if pathname == '/psysys-session':
        if current_step_data['step'] == 0:
            # Here, you might want to update anything else you need to reset
            pass  # (or remove the if clause if you don't want any reset behavior)
        return psysys_session_page
    else:
        return home_page

@app.callback(
    [Output('graph-output', 'elements'),
     Output('graph-output', 'stylesheet')],
    [Input('factor-dropdown', 'value'),
     Input('step2-dropdown1', 'value'),
     Input('step2-dropdown2', 'value'),
     Input('step3-dropdown1', 'value'),
     Input('step3-dropdown2', 'value'),
     Input('step4-dropdown', 'value')]
)
def generate_graph(selected_factors, s2d1, s2d2, s3d1, s3d2, influential_factor):
    # 1. Convert networkx graph into a dash_cytoscape format
    elements = []
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'background-color': 'blue',
                'label': 'data(label)'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle'
            }
        }
    ]

    for factor in selected_factors:
        elements.append({'data': {'id': factor, 'label': factor}})

    existing_edges = set()

    def add_edge(source, target):
        edge_key = f"{source}->{target}"  # Create a unique key for the edge
        if edge_key not in existing_edges:
            elements.append({'data': {'source': source, 'target': target}})
            existing_edges.add(edge_key)
    
    if s2d1 and len(s2d1) == 2:
        add_edge(s2d1[0], s2d1[1])

    if s2d2 and len(s2d2) == 2:
        add_edge(s2d2[0], s2d2[1])

    if s3d1 and len(s3d1) == 2:
        add_edge(s3d1[0], s3d1[1])
        add_edge(s3d1[1], s3d1[0])

    if s3d2 and len(s3d2) == 3:
        add_edge(s3d2[0], s3d2[1])
        add_edge(s3d2[1], s3d2[2])
        add_edge(s3d2[2], s3d2[0])

    # Color gradient corresponding to out-degree centrality
    # 1. Calculate the out-degree centrality
    out_degrees = {element['data']['id']: 0 for element in elements if 'id' in element['data']}

    # Then, compute out-degrees for each node
    for element in elements:
        if 'source' in element['data']:
            source = element['data']['source']
            out_degrees[source] = out_degrees.get(source, 0) + 1

    # 2. Normalize the out-degree values
    if out_degrees:  # Check if the list is not empty
        min_degree = min(out_degrees.values())
        max_degree = max(out_degrees.values())
    else:
        min_degree = 0
        max_degree = 1

    def normalize(value):
        value = float(value)
        if max_degree - min_degree == 0:
            return 0.5  
        return (value - min_degree) / (max_degree - min_degree)


    normalized_degrees = {node: normalize(degree) for node, degree in out_degrees.items()}

    # 3. Generate the color gradient
    def get_color(value):
        # The blue component remains constant at 255
        b = 255
        # Linear interpolation for the red and green components
        r = int(173 * (1 - value))
        g = int(216 * (1 - value))
        return r, g, b
    
    color_map = {node: get_color(value) for node, value in normalized_degrees.items()}

    # 4. Update the stylesheet
    for node, color in color_map.items():
        r, g, b = color
        stylesheet.append({
            'selector': f'node[id="{node}"]',
            'style': {
                'background-color': f'rgb({r},{g},{b})'
            }
        })

    # Add your influential node style
    if influential_factor:
        stylesheet.append(
            {
                'selector': f'node[id = "{influential_factor[0]}"]',
                'style': {
                    'border-color': 'red',
                    'border-width': '2px' 
                }
            }
        )

    return elements, stylesheet

if __name__ == '__main__':
    app.run_server(debug=True, port=8055)