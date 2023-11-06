# Current Version 

# Import libraries
import dash
from dash import dcc, html
from dash.exceptions import PreventUpdate
from dash import callback_context
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
app.title = "PsySys"

# Initialize factor list
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
def create_dropdown(id, options, value, placeholder, multi=True):
    return dcc.Dropdown(
        id=id,
        options=options,
        value=value,
        placeholder=placeholder,
        multi=multi,
        style={'width': '81.5%'}
    )

# Function: Generate step content based on session data
def generate_step_content(step, session_data):

    if step == 0:
        return html.Div([
            html.Br(), html.Br(), html.Br(),
            create_iframe("https://www.youtube.com/embed/d8ZZyuESXcU?si=CYvKNlf17wnzt4iG"),
            html.Br(), html.Br(),
            html.P("Please watch this video and begin with the PsySys session.")
        ])
    
    if step == 1:
        options = session_data['dropdowns']['initial-selection']['options']
        value = session_data['dropdowns']['initial-selection']['value']
        id = {'type': 'dynamic-dropdown', 'step': 1}
        text = 'Select factors'
        return html.Div([
            html.Br(), html.Br(), html.Br(),
            create_iframe("https://www.youtube.com/embed/ttLzT4U2F2I?si=xv1ETjdc1uGROZTo"),
            html.Br(), html.Br(),
            html.P("Please watch the video. Below choose the factors you are currently dealing with."),
            create_dropdown(id=id, options=options, value=value, placeholder=text),
            html.Br(),
        ])

    if step == 2:
        selected_factors = session_data['dropdowns']['initial-selection']['value'] or []
        options = [{'label': factor, 'value': factor} for factor in selected_factors]
        value_chain1 = session_data['dropdowns']['chain1']['value']
        value_chain2 = session_data['dropdowns']['chain2']['value']
        id_chain1 = {'type': 'dynamic-dropdown', 'step': 2}
        id_chain2 = {'type': 'dynamic-dropdown', 'step': 3}
        text = 'Select two factors'
        return html.Div([
            html.Br(), html.Br(), html.Br(),
            create_iframe("https://www.youtube.com/embed/stqJRtjIPrI?si=1MI5daW_ldY3aQz3"),
            html.Br(), html.Br(),
            html.P("Please watch the video. Below indicate two causal relations you recognize."),
            html.P("Example: If you feel that normally worrying causes you to become less concentrated, select these factors below in this order.", style={'width': '70%', 'font-style': 'italic', 'color': 'grey'}),
            create_dropdown(id=id_chain1, options=options, value=value_chain1, placeholder=text),
            html.Br(),
            create_dropdown(id=id_chain2, options=options, value=value_chain2, placeholder=text),
            html.Br()
        ])
    
    if step == 3:
        selected_factors = session_data['dropdowns']['initial-selection']['value'] or []
        options = [{'label': factor, 'value': factor} for factor in selected_factors]
        value_cycle1 = session_data['dropdowns']['cycle1']['value']
        value_cycle2 = session_data['dropdowns']['cycle2']['value']
        id_cycle1 = {'type': 'dynamic-dropdown', 'step': 4}
        id_cycle2 = {'type': 'dynamic-dropdown', 'step': 5}
        text1 = 'Select two factors that reinforce each other'
        text2 = 'Select three factors that reiforce each other'
        return html.Div([
            html.Br(), html.Br(), html.Br(),
            create_iframe('https://www.youtube.com/embed/EdwiSp3BdKk?si=TcqeWxAlGl-_NUfx'),
            html.Br(), html.Br(),
            html.P("Please watch the video. Below indicate your vicious cycles. You can choose one containing two factors and another one containing three.", style={'width': '70%'}),
            create_dropdown(id=id_cycle1, options=options, value=value_cycle1, placeholder=text1),
            html.Br(),
            create_dropdown(id=id_cycle2, options=options, value=value_cycle2, placeholder=text2),
            html.Br()
        ])
    
    if step == 4:
        selected_factors = session_data['dropdowns']['initial-selection']['value'] or []
        options = [{'label': factor, 'value': factor} for factor in selected_factors]
        value_target = session_data['dropdowns']['target']['value']
        id = {'type': 'dynamic-dropdown', 'step': 6}
        text = 'Select one factor'
        return html.Div([
            html.Br(), html.Br(), html.Br(),
            create_iframe('https://www.youtube.com/embed/hwisVnJ0y88?si=OpCWAMaDwTThocO6'),
            html.Br(), html.Br(),
            html.P("Please watch the video. Below indicate the factor you feel is the most influential one in your mental-health map.", style={'width': '70%'}),
            create_dropdown(id=id, options=options, value=value_target, placeholder=text),
            html.Br()
        ])

    if step == 5:
        elements = session_data.get('elements', [])
        return html.Div([
            html.Br(), html.Br(), html.Br(),
            cyto.Cytoscape(
                id='graph-output', 
                elements=elements,
                layout={'name': 'cose', 'fit': True, 'padding': 10},
                zoom=1,
                pan={'x': 200, 'y': 200},
                stylesheet=stylesheet,
                style={'width': '70%', 'height': '500px'}
            ),
            html.Br()
        ])
    
    else:
        return None

# Define style to initiate components
hidden_style = {'display': 'none'}
visible_style = {'display': 'block'}

# Layout elements: Next & Back button
button_group = html.Div(
    [
        dbc.Button("Back", id='back-button', n_clicks=0, style=hidden_style),
        dbc.Button("Next", id='next-button', n_clicks=0, style=hidden_style)
    ],
    style={
        'display': 'flex',
        'justifyContent': 'center',  # Centers the buttons horizontally
        'gap': '10px',               # Adds space between the buttons
    }
)

# Layout elements: Navigation sidebar
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

# Layout elements: Page content
content_col = dbc.Col(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
        button_group
    ],
    md=10,
)

# Define app layout
app.layout = dbc.Container([
    dbc.Row([nav_col, content_col]),
    dcc.Store(id='current-step', data={'step': 0}, storage_type='local'),
    html.Div(id='hidden-div', style={'display': 'none'}),
    dcc.Store(id='session-data', data={
        'dropdowns': {
            'initial-selection': {'options':[{'label': factor, 'value': factor} for factor in factors], 'value': None},
            'chain1': {'options':[], 'value': None},
            'chain2': {'options':[], 'value': None},
            'cycle1': {'options':[], 'value': None},
            'cycle2': {'options':[], 'value': None},
            'target': {'options':[], 'value': None},
            },
        'elements': []
    }, storage_type='session')
])

# Define content for Home tab
home_page = html.Div([
    html.H1("Welcome to PsySys App!"),
    html.P("This is the Home tab. More content to come!"),
])

# Stylesheet for network 
stylesheet = [{'selector': 'node','style': {'background-color': 'blue', 'label': 'data(label)'}},
              {'selector': 'edge','style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
    ]

# Callback: Display the page & next/back button based on current step 
@app.callback(
    [Output('page-content', 'children'),
     Output('back-button', 'style'),
     Output('next-button', 'style'),
     Output('next-button', 'children')],
    [Input('url', 'pathname'),
     Input('current-step', 'data')],
    [State('session-data', 'data')]
)
def update_page_and_buttons(pathname, current_step_data, session_data):
    step = current_step_data.get('step', 0)  # Default to step 0 if not found

    # Default button states
    back_button_style = hidden_style
    next_button_style = visible_style
    next_button_text = "Next"

    # Update content and button states based on the pathname and step
    if pathname == '/':
        content = home_page
        next_button_style = hidden_style  # Both buttons hidden
    elif pathname == '/psysys-session':
        # Check the step and update accordingly
        if step == 0:
            content = generate_step_content(step, session_data)
            next_button_text = "Start"       # Change text to "Start"
        elif step == 1:
            content = generate_step_content(step, session_data)
        elif 2 <= step <= 4:
            content = generate_step_content(step, session_data)
            back_button_style = visible_style            # Show back button
            next_button_style = visible_style            # Show next button
        elif step == 5:
            content = generate_step_content(step, session_data)
            back_button_style = visible_style           # Show back button
            next_button_text = "Redo"         # Change text to "Redo"

    return content, back_button_style, next_button_style, next_button_text
    
# Callback: Update current step based on next/back button clicks
@app.callback(
    Output('current-step', 'data'),
    [Input('back-button', 'n_clicks'),
     Input('next-button', 'n_clicks')],
    [State('current-step', 'data')]
)
def update_step(back_clicks, next_clicks, current_step_data):
    # Initialize click counts to 0 if None
    back_clicks = back_clicks or 0
    next_clicks = next_clicks or 0

    # Use callback_context to determine which input has been triggered
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "back-button.n_clicks" in changed_id:
        # Decrement the step, ensuring it doesn't go below 0
        current_step_data['step'] = max(current_step_data['step'] - 1, 0)
    elif "next-button.n_clicks" in changed_id:
        # Increment the step, if it reaches the max step reset to 0
        if current_step_data['step'] >= 5:
            current_step_data['step'] = 0
        else:
            current_step_data['step'] += 1

    return current_step_data

# Callback: Update session data based on user input
@app.callback(
    Output('hidden-div', 'children'),
    Input({'type': 'dynamic-dropdown', 'step': ALL}, 'value')
)
def update_hidden_div(values):
    # Convert values to JSON and return
    return json.dumps(values)

# Callback for updating session-data (dropdowns) based on hidden Div
@app.callback(
    Output('session-data', 'data'),
    Input('hidden-div', 'children'),
    [State('session-data', 'data'),
     State('current-step', 'data')]
)
def update_session_data(json_values, session_data, current_step_data):

    step = current_step_data.get('step')
    values = json.loads(json_values) if json_values else []

    if len(values) == 1:
        if step == 1:
            session_data['dropdowns']['initial-selection']['value'] = values[0]
        elif step == 4:
            session_data['dropdowns']['target']['value'] = values[0]

    elif len(values) == 2:
        if step == 2: 
            session_data['dropdowns']['chain1']['value'] = values[0]
            session_data['dropdowns']['chain2']['value'] = values[1]
        elif step == 3: 
            session_data['dropdowns']['cycle1']['value'] = values[0]
            session_data['dropdowns']['cycle2']['value'] = values[1]

    return session_data

# Callback: Update session data based on current step (reset if 0)
@app.callback(
    [Output('session-data', 'data', allow_duplicate=True)],
    Input('current-step', 'data'),
    prevent_initial_call=True
)
def reset(current_step_data):
    if current_step_data['step'] == 0:
        data = {
            'dropdowns': {
                'initial-selection': {'options': [{'label': factor, 'value': factor} for factor in factors], 'value': None},
                'chain1': {'options': [], 'value': None},
                'chain2': {'options': [], 'value': None},
                'cycle1': {'options': [], 'value': None},
                'cycle2': {'options': [], 'value': None},
                'target': {'options': [], 'value': None},
            },
            'elements': []
        }
        return (data,) 

    else:
        return (dash.no_update,)  

# Callback: Generate mental-health map
@app.callback(
    [Output('graph-output', 'elements'),
     Output('graph-output', 'stylesheet')],
    [Input('session-data', 'data')]
)
def generate_graph(session_data):

    selected_factors = session_data['dropdowns']['initial-selection']['value'] or []
    s2d1 = session_data['dropdowns']['chain1']['value']
    s2d2 = session_data['dropdowns']['chain2']['value']
    s3d1 = session_data['dropdowns']['cycle1']['value']
    s3d2 = session_data['dropdowns']['cycle2']['value']
    influential_factor = session_data['dropdowns']['target']['value']

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

    # Add influential node style
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
    app.run_server(debug=True, port=8001)