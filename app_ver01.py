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
import uuid

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],suppress_callback_exceptions=True)
app.title = "PsySys"

# Initialize factor list
factors = ["Loss of interest", "Feeling down", "Stress", "Worry", "Overthinking", "Sleep problems", 
           "Joint pain", "Changes in appetite", "Self-blame", "Trouble concentrating", "Procrastinating", 
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
        selected_factors = session_data['add-nodes'] or []
        options = [{'label': factor, 'value': factor} for factor in selected_factors]
        return html.Div([
            html.Div([
                # Graph Container
                html.Div([
                    cyto.Cytoscape(
                        id='graph-output',
                        elements=session_data['elements'],
                        layout={'name': 'cose', 'fit': True, 'padding': 10},
                        zoom=1,
                        pan={'x': 200, 'y': 200},
                        stylesheet = session_data['stylesheet'],
                        style={'width': '90%', 'height': '480px'}
                    )
                ], style={'flex': '1'}),

                # Add Node UI Container
                html.Div([
                    # Div for adding nodes
                    html.Div([
                        dbc.Input(id='input-node-name', type='text', placeholder='Enter new factor', style={'marginRight': '10px', 'borderRadius': '10px'}),
                        dbc.Button("➕", id='btn-add-node', color="primary"),
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),  # Spacing between add and delete rows

                    # Div for deleting nodes
                    html.Div([
                        dbc.Input(id='input-delete-node', type='text', placeholder='Enter factor to delete', style={'marginRight': '10px', 'borderRadius': '10px'}),
                        dbc.Button("➖", id='btn-delete-node', color="danger"),
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '25px'}),

                    # Div for adding edges
                    html.Div([
                        dcc.Dropdown(id='input-add-edge', options=options, placeholder='Enter new connection', multi=True, style={'width': '96%', 'borderRadius': '10px'}),
                        dbc.Button("➕", id='btn-add-edge', color="primary"),
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

                    # Div for deleting edges
                    html.Div([
                        dcc.Dropdown(id='input-delete-edge', options=options, placeholder='Enter connection to delete', multi=True, style={'width': '96%', 'borderRadius': '10px'}),
                        dbc.Button("➖", id='btn-delete-edge', color="danger"),
                    ], style={'display': 'flex', 'alignItems': 'center'}),

                    ], style={'width': '300px', 'padding': '10px', 'marginTop': '80px'}),
                ], style={'display': 'flex', 'height': '470px', 'alignItems': 'flex-start', 'marginTop': '80px'}),
                html.Br(),
                ])
    
    else:
        return None

# Function: Initiate graph with elements
def map_add_factors(session_data):
    selected_factors = session_data['dropdowns']['initial-selection']['value'] or []
    map_elements = [{'data': {'id': factor, 'label': factor}} for factor in selected_factors]
    session_data['elements'] = map_elements
    return session_data

# Function: Add an edge 
def add_edge(source, target, elements, existing_edges):
        edge_key = f"{source}->{target}"
        if edge_key not in existing_edges:
            elements.append({'data': {'source': source, 'target': target}})
            existing_edges.add(edge_key)
            return elements, existing_edges
        
# Function: Delete an edge
def delete_edge(source, target, elements, existing_edges):
    edge_key = f"{source}->{target}"
    if edge_key in existing_edges:
        for i in range(len(elements) - 1, -1, -1):
            if elements[i].get('data', {}).get('source') == source and elements[i].get('data', {}).get('target') == target:
                del elements[i]
                break
        existing_edges.remove(edge_key)
    return elements, existing_edges

# Function: Include causal chains into the map  
def map_add_chains(session_data):
    map_elements = session_data['elements']
    chain1_elements = session_data['dropdowns']['chain1']['value']
    chain2_elements = session_data['dropdowns']['chain2']['value']
    existing_edges = set(session_data['edges'])
    if chain1_elements and len(chain1_elements) == 2:
        add_edge(chain1_elements[0], chain1_elements[1], map_elements, existing_edges)
    if chain2_elements and len(chain2_elements) == 2:
        add_edge(chain2_elements[0], chain2_elements[1], map_elements, existing_edges)
    session_data['elements'] = map_elements
    session_data['edges'] = list(existing_edges)
    return session_data, existing_edges

# Function: Add vicious cycles into the map 
def map_add_cycles(session_data):
    map_elements = session_data['elements']
    cycle1_elements = session_data['dropdowns']['cycle1']['value']
    cycle2_elements = session_data['dropdowns']['cycle2']['value']
    existing_edges = set(session_data['edges'])
    if cycle1_elements and len(cycle1_elements) == 2:
        add_edge(cycle1_elements[0], cycle1_elements[1], map_elements, existing_edges)
        add_edge(cycle1_elements[1], cycle1_elements[0], map_elements, existing_edges)
    if cycle2_elements and len(cycle2_elements) == 3:
        add_edge(cycle2_elements[0], cycle2_elements[1], map_elements, existing_edges)
        add_edge(cycle2_elements[1], cycle2_elements[2], map_elements, existing_edges)
        add_edge(cycle2_elements[2], cycle2_elements[0], map_elements, existing_edges)
    session_data['elements'] = map_elements
    session_data['edges'] = list(existing_edges)
    return session_data
        
def normalize(value, max_degree, min_degree):
        value = float(value)
        if max_degree - min_degree == 0:
            return 0.5  
        
        return (value - min_degree) / (max_degree - min_degree)

# Function: Color graph (out-degree centrality, target node)
def graph_color(session_data):
    map_elements = session_data['elements']
    influential_factor = session_data['dropdowns']['target']['value']
    stylesheet = [{'selector': 'node','style': {'background-color': 'blue', 'label': 'data(label)'}},
              {'selector': 'edge','style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
    ]

    out_degrees = {element['data']['id']: 0 for element in map_elements if 'id' in element['data']}

    # Then, compute out-degrees for each node
    for element in map_elements:
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

    normalized_degrees = {node: normalize(degree, max_degree, min_degree) for node, 
                          degree in out_degrees.items()}

    # 3. Generate the color gradient
    def get_color(value):
        b = 255
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

    session_data['stylesheet'] = stylesheet
    return session_data

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
                dbc.NavLink("Psychoeducation", href="/psysys-session", active="exact"),
                dbc.NavLink("My mental-health map")
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

# Stylesheet for network 
stylesheet = [{'selector': 'node','style': {'background-color': 'blue', 'label': 'data(label)'}},
              {'selector': 'edge','style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
    ]

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
        'elements': [], 
        'stylesheet': stylesheet,
        'edges': [],
        'add-nodes': [],
        'add-edges': []
    }, storage_type='session')
])

# Define content for Home tab
home_page = html.Div([
    html.H1("Welcome to PsySys App!"),
    html.P("This is the Home tab. More content to come!"),
    html.Div([
        cyto.Cytoscape(
            id='graph-output-home', 
            elements=[],
            layout={'name': 'cose', 'fit': True, 'padding': 10},
            zoom=1,
            pan={'x': 200, 'y': 200},
            stylesheet=stylesheet,
            style={'width': '70%', 'height': '500px'}
        ),
    ])
])

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
            map_add_factors(session_data)
        elif step == 4:
            session_data['dropdowns']['target']['value'] = values[0]
            graph_color(session_data)

    elif len(values) == 2:
        if step == 2: 
            session_data['dropdowns']['chain1']['value'] = values[0]
            session_data['dropdowns']['chain2']['value'] = values[1]
            map_add_chains(session_data)
        elif step == 3: 
            session_data['dropdowns']['cycle1']['value'] = values[0]
            session_data['dropdowns']['cycle2']['value'] = values[1]
            map_add_cycles(session_data)

    return session_data

# Callback: Update session data based on initial factor selection
@app.callback(
     Output('session-data', 'data', allow_duplicate=True),
     Input('factor-dropdown', 'value'),
     State('session-data', 'data'),
     prevent_initial_call = True

)
def dropdown_step5_init(value, session_data):
    if session_data['add-node'] == []:
        session_data['add-node'] = value
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
            'elements': [],
            'edges': [],
            'add-nodes': [],
            'add-edges': [],
            'stylesheet': stylesheet
        }
        return (data,) 

    else:
        return (dash.no_update,)  

# Callback: Add additional node to graph 
@app.callback(
    [Output('graph-output', 'elements'),
     Output('input-add-edge', 'options'),
     Output('input-delete-edge', 'options'),
     Output('session-data', 'data', allow_duplicate=True)],
    [Input('btn-add-node', 'n_clicks')],
    [State('input-node-name', 'value'),
     State('graph-output', 'elements'),
     State('session-data', 'data')],
     prevent_initial_call = True
)
def add_node(n_clicks, node_name, elements, session_data): 
    # Else append new node name to add-node list
    if n_clicks and node_name:
        # Ensure the node doesn't already exist
        if not any(node['data']['id'] == node_name for node in elements):
            new_node = {
                'data': {'id': node_name, 'label': node_name},
                'style': {'background-color': 'grey'}
            }
            elements.append(new_node)

    # Extract all node names
    node_names = [node['data']['id'] for node in elements if 'id' in node['data'] and len(node['data']['id']) < 30]
    session_data['add-nodes'] = node_names

    return elements, node_names, node_names, session_data

# Callback: Remove existing node from graph
@app.callback(
    [Output('graph-output', 'elements', allow_duplicate=True),
     Output('input-add-edge', 'options', allow_duplicate=True),
     Output('input-delete-edge', 'options', allow_duplicate=True),
     Output('session-data', 'data', allow_duplicate=True)],
    [Input('btn-delete-node', 'n_clicks')],
    [State('input-delete-node', 'value'),
     State('graph-output', 'elements'),
     State('session-data', 'data')],
     prevent_initial_call=True
)
def delete_node(n_clicks, node_id, elements, session_data):
    if n_clicks and node_id:
        elements = [node for node in elements if node['data'].get('id') != node_id]

    # Extract all node names
    node_names = [node['data']['id'] for node in elements if 'id' in node['data'] and len(node['data']['id']) < 30]
    session_data['add-nodes'] = node_names

    return elements, node_names, node_names, session_data

# Callback: Restrict add and delete edge dropdowns to max 2 values
@app.callback(
    Output('input-add-edge', 'value'),
    Input('input-add-edge', 'value')
)
def limit_dropdown_add_edge(add_edge):
    if add_edge and len(add_edge) > 2:
        return add_edge[:2]
    return add_edge

@app.callback(
    Output('input-delete-edge', 'value'),
    Input('input-delete-edge', 'value')
)
def limit_dropdown_delete_edge(delete_edge):
    if delete_edge and len(delete_edge) > 2:
        return delete_edge[:2]
    return delete_edge

# Callback: Add additional edge to graph
@app.callback(
    [Output('graph-output', 'elements', allow_duplicate=True),
     Output('session-data', 'data', allow_duplicate=True)],
    [Input('btn-add-edge', 'n_clicks')],
    [State('input-add-edge', 'value'),
     State('graph-output', 'elements'),
     State('session-data', 'data')],
     prevent_initial_call=True
)

def add_edge_output(n_clicks, new_edge, elements, session_data):
    if n_clicks and new_edge:
        source = new_edge[0]
        target = new_edge[1]
        existing_edges = set(session_data['edges'])
        add_edge(source, target, elements, existing_edges)
        session_data['edges'] = list(existing_edges)
    return elements, session_data

# Callback: Delete existing edge from graph
@app.callback(
    [Output('graph-output', 'elements', allow_duplicate=True),
     Output('session-data', 'data', allow_duplicate=True)],
    [Input('btn-delete-edge', 'n_clicks')],
    [State('input-delete-edge', 'value'),
     State('graph-output', 'elements'),
     State('session-data', 'data')],
     prevent_initial_call=True
)

def delete_edge_output(n_clicks, edge, elements, session_data):
    if n_clicks and edge:
        source = edge[0]
        target = edge[1]
        existing_edges = set(session_data['edges'])
        delete_edge(source, target, elements, existing_edges)
        session_data['edges'] = list(existing_edges)
    return elements, session_data

# Callback: Update session data based on graph output when clicking 'Save' button


# INCLUDE GRAPH INFORMATION IN SESSION-DATA (**)
# Button - re-calculate centrality triggering session-data (**)

# 'DOWNLOAD' OPTION
# INLCUDE MAP IN HOME TAB (**)
# PROGRESS BAR

if __name__ == '__main__':
    app.run_server(debug=True, port=8069)