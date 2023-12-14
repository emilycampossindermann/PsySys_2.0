# Current Version mental-health map tab

from constants import factors, node_color, node_size
from functions import generate_step_content, create_mental_health_map_tab, create_likert_scale, create_iframe, create_dropdown
from functions import map_add_chains, map_add_cycles, map_add_factors, add_edge, delete_edge, graph_color, color_scheme, node_sizing
from functions import apply_centrality_color_styles, apply_centrality_size_styles, apply_severity_color_styles, apply_severity_size_styles, apply_uniform_color_styles, apply_uniform_size_styles

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
import base64

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],suppress_callback_exceptions=True)
app.title = "PsySys"

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

buttons_map = html.Div(
    [
        dbc.Button("Load from session", id='load', n_clicks=0, style=hidden_style),
        dbc.Button("Upload", id='upload', n_clicks=0, style=hidden_style),
        dbc.Button("Download", id='download', n_clicks=0, style=hidden_style)
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
                dbc.NavLink("Edit My Map", href="/my-mental-health-map", active="exact"),
                dbc.NavLink("Track My Map", href="/track-my-mental-health-map", active="exact")
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
        button_group,
        buttons_map
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
    dcc.Store(id='current-step', data={'step': 0}, storage_type='session'),
    dcc.Store(id='color_scheme', data=None, storage_type='session'),
    dcc.Store(id='sizing_scheme', data=None, storage_type='session'),
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
        'edges': [],
        'add-nodes': [],
        'add-edges': [],
        'stylesheet': stylesheet,
        'annotations': []
    }, storage_type='session'),
    dcc.Store(id='edit-map-data', data={
        'dropdowns': {
            'initial-selection': {'options':[{'label': factor, 'value': factor} for factor in factors], 'value': None},
            'chain1': {'options':[], 'value': None},
            'chain2': {'options':[], 'value': None},
            'cycle1': {'options':[], 'value': None},
            'cycle2': {'options':[], 'value': None},
            'target': {'options':[], 'value': None},
            },
        'elements': [], 
        'edges': [],
        'add-nodes': [],
        'add-edges': [],
        'stylesheet': stylesheet,
        'annotations': []
    }, storage_type='session'),
    dcc.Store(id='severity-scores', data={}, storage_type='session'),
    dcc.Store(id='annotation-data', data={}, storage_type='session'),
    dcc.Store(id='edge-data', data={}, storage_type='session'),
    dcc.Download(id='download-link')
])

# Define content for Home tab
home_page = html.Div([
    html.H1("Welcome to PsySys App!"),
    html.P("This is the Home tab. More content to come!")
])

# Callback: Display the page & next/back button based on current step 
@app.callback(
    [Output('page-content', 'children'),
     Output('back-button', 'style'),
     Output('next-button', 'style'),
     Output('next-button', 'children')],
    [Input('url', 'pathname'),
     Input('edit-map-data', 'data'),  # Add this input
     Input('current-step', 'data')],
    [State('session-data', 'data'),
     State('color_scheme', 'data'),
     State('sizing_scheme', 'data')]
)
def update_page_and_buttons(pathname, edit_map_data, current_step_data, session_data, color, sizing):
    step = current_step_data.get('step', 0)  # Default to step 0 if not found

    # Default button states
    content = None
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

    elif pathname == "/my-mental-health-map":
        content = create_mental_health_map_tab(edit_map_data, color, sizing)
        back_button_style = hidden_style
        next_button_style = hidden_style

    elif content is None:
        content = html.Div("Page not found")

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
    return json.dumps(values)

# Callback: Update session-data (dropdowns) based on hidden Div
@app.callback(
    Output('session-data', 'data'),
    [Input('next-button', 'n_clicks'),
    Input('hidden-div', 'children')],
    [State('session-data', 'data'),
     State('current-step', 'data'),
     State('severity-scores', 'data')]
)
def update_session_data(n_clicks, json_values, session_data, current_step_data, severity_scores):

    step = current_step_data.get('step')
    values = json.loads(json_values) if json_values else []

    if len(values) == 1:
            if step == 1:
                session_data = map_add_factors(session_data, values[0], severity_scores)
                #session_data['dropdowns']['initial-selection']['value'] = values[0]
                #map_add_factors(session_data)

    if n_clicks: 
        if len(values) == 1:
            # if step == 1:
            #     session_data = map_add_factors(session_data, values[0], severity_scores)
            #     print(session_data['dropdowns']['initial-selection']['value'])
            #     print(severity_scores)
            #     #session_data['dropdowns']['initial-selection']['value'] = values[0]
            #     #map_add_factors(session_data)
            if step == 4:
                session_data['dropdowns']['target']['value'] = values[0]
                graph_color(session_data, severity_scores)

        elif len(values) == 2:
            if step == 2: 
                session_data = map_add_chains(session_data, values[0], values[1])
                #session_data['dropdowns']['chain1']['value'] = values[0]
                #session_data['dropdowns']['chain2']['value'] = values[1]
                #print(session_data['edges'])
                #map_add_chains(session_data)
            elif step == 3: 
                #session_data['dropdowns']['cycle1']['value'] = values[0]
                #session_data['dropdowns']['cycle2']['value'] = values[1]
                session_data = map_add_cycles(session_data, values[0], values[1])

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

# Callback: Reset session data & severity data at "Redo" (step 0)
@app.callback(
    [Output('session-data', 'data', allow_duplicate=True),
     Output('severity-scores', 'data', allow_duplicate=True)],
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
            'stylesheet': stylesheet,
            'annotations': []
        }
        return (data, {}) 

    else:
        return (dash.no_update, dash.no_update)  

# Callback: Set edit-graph to session-data if "Load from session" is pressed
@app.callback(
    Output('edit-map-data', 'data'),
    Input('load-map-btn', 'n_clicks'),
    State('session-data', 'data')
)
def load_session_graph(n_clicks, session_data):
    if n_clicks:
        return session_data
    # Return no update if the button wasn't clicked
    return dash.no_update      

# Callback: Download graph as file
@app.callback(
    Output('download-link', 'data'),
    Input('download-file-btn', 'n_clicks'),
    State('edit-map-data', 'data'),
    prevent_initial_call=True
)
def generate_download(n_clicks, data):
    if n_clicks:
        # Convert the dictionary to a JSON string
        json_string = json.dumps(data)
        return dcc.send_bytes(json_string.encode('utf-8'), "my_mental_health_map.json")
    return dash.no_update

# Callback: Upload existing map file
@app.callback(
    Output('edit-map-data', 'data', allow_duplicate=True),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def upload_graph(contents, filename):
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        # Assuming the file is JSON, adjust the decoding as necessary
        data = json.loads(decoded.decode('utf-8'))
        return data
    return dash.no_update

# Callback: Open edit node modal upon clicking it
@app.callback(
    [Output('node-edit-modal', 'is_open'),
     Output('modal-node-name', 'value'),
     Output('modal-severity-score', 'value'),
     Output('note-input', 'value')],
    [Input('my-mental-health-map', 'tapNodeData'),
     Input('inspect-switch', 'value'),
     Input('severity-scores', 'data'),
     State('annotation-data', 'data')],  
    prevent_initial_call=True
)
def open_node_edit_modal(tapNodeData, switch, severity_scores, annotations):
    if 0 not in switch and tapNodeData:
        node_id = tapNodeData['id']
        node_name = tapNodeData.get('label', node_id)
        severity_score = severity_scores.get(node_name, 0)
        annotation = annotations.get(node_id, '') 

        return True, node_name, severity_score, annotation
    return False, None, None, ''

# Reset tabnodedata on mode switch
@app.callback(
    Output('my-mental-health-map', 'tapNodeData'),  # Assuming 'tabNode' is the component storing the node data
    Input('inspect-switch', 'value'),  # Assuming 'mode-switch' keeps track of the current mode
    prevent_initial_call=True
)
def reset_node_data_on_click(switch):
    return {}

# Callback: Update the annotation for the node
@app.callback(
    Output('annotation-data', 'data'),
    [Input('note-input', 'value')],
    [State('my-mental-health-map', 'tapNodeData'),
     State('annotation-data', 'data')]
)
def update_annotations(note_input, tapNodeData, annotations):
    if tapNodeData:
        node_id = tapNodeData['id']
        annotations[node_id] = note_input 
    return annotations

# Callback: Save node edits (name & severity) in graph and edit_map_data
@app.callback(
    [Output('my-mental-health-map', 'elements', allow_duplicate=True),
     Output('severity-scores', 'data', allow_duplicate=True),
     Output('edit-map-data', 'data', allow_duplicate=True)],
    [Input('modal-save-btn', 'n_clicks')],
    [State('modal-node-name', 'value'),
     State('modal-severity-score', 'value'),
     State('my-mental-health-map', 'elements'),
     State('severity-scores', 'data'),
     State('edit-map-data', 'data'),
     State('my-mental-health-map', 'tapNodeData')],
    prevent_initial_call=True
)
def save_node_changes(n_clicks, new_name, new_severity, elements, severity_scores, edit_map_data, tapNodeData):
    if n_clicks and tapNodeData:
        old_node_id = tapNodeData['id']
        old_node_name = tapNodeData.get('label', old_node_id)  # Assuming label is stored in tapNodeData

        # Update node name in elements
        for element in elements:
            if element.get('data', {}).get('id') == old_node_id:
                element['data']['label'] = new_name

        # Update node name in severity_scores if it's changed
        if old_node_name != new_name:
            severity_scores[new_name] = severity_scores.pop(old_node_name, new_severity)

        # Update severity score
        severity_scores[new_name] = new_severity

        # Update edit_map_data with the changed elements
        edit_map_data['elements'] = elements

        return elements, severity_scores, edit_map_data
    return dash.no_update

# Callback to open the modal
@app.callback(
    [Output('edge-edit-modal', 'is_open'),
     Output('edge-explanation', 'children'),
     Output('edge-strength', 'value'),
     Output('edge-annotation', 'value')],
    [Input('my-mental-health-map', 'tapEdgeData'),
     Input('inspect-switch', 'value')],
    State('edge-data', 'data'),
    prevent_initial_call=True
)
def open_edge_edit_modal(tapEdgeData, switch, edge_data):
    if edge_data is None:
        edge_data = {}

    if 0 not in switch and tapEdgeData:
        edge_id = tapEdgeData['id']
        explanation = f"The factor {tapEdgeData['source']} causes the factor {tapEdgeData['target']}"
        strength = edge_data.get(edge_id, {}).get('strength', 5)
        annotation = edge_data.get(edge_id, {}).get('annotation', '')
        return True, explanation, strength, annotation

    return False, '', 5, ''

# Combined callback to update the edge data and close the modal
@app.callback(
    [Output('edge-data', 'data', allow_duplicate=True),
     Output('edge-edit-modal', 'is_open', allow_duplicate=True),
     Output('my-mental-health-map', 'stylesheet', allow_duplicate=True)],
    [Input('edge-save-btn', 'n_clicks'),
     Input('my-mental-health-map', 'tapEdgeData'),
     Input('inspect-switch', 'value')],
    [State('edge-strength', 'value'),
     State('edge-annotation', 'value'),
     State('edge-data', 'data'),
     State('edge-edit-modal', 'is_open'),
     State('edit-map-data', 'data'),
     State('my-mental-health-map', 'stylesheet')],
     prevent_initial_call=True
)
def update_edge_data_and_close_modal(save_clicks, tapEdgeData, switch, strength, annotation, edge_data, is_open, edit_map_data, current):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Ensure edge_data and edit_map_data['stylesheet'] are initialized
    if edge_data is None:
        edge_data = {}
    #stylesheet = edit_map_data.get('stylesheet', []) if edit_map_data else []
    stylesheet=current

    if triggered_id == 'edge-save-btn' and tapEdgeData:
        edge_id = tapEdgeData['id']
        # Update the edge data
        edge_data[edge_id] = {
            'strength': strength,
            'annotation': annotation
        }

        # Update the stylesheet for the tapped edge
        opacity = strength / 5  # Adjust opacity based on strength
        tapped_edge_style = {
            'selector': f'edge[id="{edge_id}"]',
            'style': {'opacity': opacity}
        }
        # Create a new stylesheet with updated style for the tapped edge
        new_stylesheet = [rule for rule in stylesheet if rule['selector'] != f'edge[id="{edge_id}"]']
        new_stylesheet.append(tapped_edge_style)

        return edge_data, False, new_stylesheet  # Close the modal and update stylesheet

    if triggered_id == 'my-mental-health-map' and 0 not in switch and tapEdgeData:
        edge_id = tapEdgeData['id']
        strength = edge_data.get(edge_id, {}).get('strength', 5)
        annotation = edge_data.get(edge_id, {}).get('annotation', '')
        return edge_data, True, stylesheet  # Open the modal without updating stylesheet

    return edge_data, is_open, stylesheet  # Default return

# Callback: Edit map - add node
@app.callback(
    [Output('my-mental-health-map', 'elements'),
     Output('edit-edge', 'options'),
     Output('edit-map-data', 'data', allow_duplicate=True),
     Output('severity-scores', 'data', allow_duplicate=True)],  # Add this output
    [Input('btn-plus-node', 'n_clicks')],
    [State('edit-node', 'value'),
     State('my-mental-health-map', 'elements'),
     State('edit-map-data', 'data'),
     State('severity-scores', 'data')],  # Add this state
     prevent_initial_call=True
)
def map_add_node(n_clicks, node_name, elements, edit_map_data, severity_scores):
    if n_clicks and node_name:
        if not any(node['data']['id'] == node_name for node in elements):
            new_node = {'data': {'id': node_name, 'label': node_name}}
            elements.append(new_node)
            severity_scores[node_name] = 5  # Add new node with default severity score

    node_names = [node['data']['id'] for node in elements if 'id' in node['data'] and len(node['data']['id']) < 30]
    edit_map_data['add-nodes'] = node_names
    edit_map_data['elements'] = elements

    return elements, node_names, edit_map_data, severity_scores

# Callback: Remove existing node from graph
@app.callback(
    [Output('my-mental-health-map', 'elements', allow_duplicate=True),
     Output('edit-edge', 'options', allow_duplicate=True),
     Output('edit-map-data', 'data', allow_duplicate=True),
     Output('severity-scores', 'data', allow_duplicate=True)],  # Add this output
    [Input('btn-minus-node', 'n_clicks')],
    [State('edit-node', 'value'),
     State('my-mental-health-map', 'elements'),
     State('edit-map-data', 'data'),
     State('severity-scores', 'data')],  # Add this state
     prevent_initial_call=True
)
def delete_node(n_clicks, node_id, elements, edit_map_data, severity_scores):
    if n_clicks and node_id:
        # Delete node from elements
        elements = [element for element in elements if element['data'].get('id') != node_id]
        # Delete any existing edges from elements which contain this node
        elements = [element for element in elements if not (('source' in element['data'] and element['data']['source'] == node_id) or ('target' in element['data'] and element['data']['target'] == node_id))]

        if node_id in severity_scores:
            del severity_scores[node_id]  # Remove node from severity scores

    node_names = [node['data']['id'] for node in elements if 'id' in node['data'] and len(node['data']['id']) < 30]
    edit_map_data['add-nodes'] = node_names
    edit_map_data['elements'] = elements

    print(severity_scores)
    return elements, node_names, edit_map_data, severity_scores

# Callback: Limit dropdown for edit-edge to 2
@app.callback(
    Output('edit-edge', 'value'),
    Input('edit-edge', 'value')
)
def limit_dropdown_edit_edge(edit_edge):
    if edit_edge and len(edit_edge) > 2:
        return edit_edge[:2]
    return edit_edge

# Callback: Add additional edge to graph
# @app.callback(
#     [Output('my-mental-health-map', 'elements', allow_duplicate=True),
#      Output('edit-map-data', 'data', allow_duplicate=True)],
#     [Input('btn-plus-edge', 'n_clicks')],
#     [State('edit-edge', 'value'),
#      State('my-mental-health-map', 'elements'),
#      State('edit-map-data', 'data')],
#      prevent_initial_call=True
# )
# def add_edge_output(n_clicks, new_edge, elements, edit_map_data):
#     if n_clicks and new_edge and len(new_edge) == 2:
#         source = new_edge[0]
#         target = new_edge[1]
#         existing_edges = set(edit_map_data['edges'])
#         add_edge(source, target, elements, existing_edges)
#         edit_map_data['edges'] = list(existing_edges)
#         edit_map_data['elements'] = elements
#     return elements, edit_map_data
@app.callback(
    [Output('my-mental-health-map', 'elements', allow_duplicate=True),
     Output('edit-map-data', 'data', allow_duplicate=True)],
    [Input('btn-plus-edge', 'n_clicks')],
    [State('edit-edge', 'value'),
     State('my-mental-health-map', 'elements'),
     State('edit-map-data', 'data')],
     prevent_initial_call=True
)
def add_edge_output(n_clicks, new_edge, elements, edit_map_data):
    if n_clicks and new_edge and len(new_edge) == 2:
        source, target = new_edge
        # Assuming edit_map_data['edges'] is a list of edge dictionaries
        existing_edges = set(f"{e['data']['source']}->{e['data']['target']}" for e in elements if 'source' in e.get('data', {}))

        add_edge(source, target, elements, existing_edges)

        edit_map_data['edges'] = [{'data': {'source': source, 'target': target}} for source, target in (edge.split('->') for edge in existing_edges)]
        edit_map_data['elements'] = elements

    return elements, edit_map_data


# Callback: Delete existing edge from graph
# @app.callback(
#     [Output('my-mental-health-map', 'elements', allow_duplicate=True),
#      Output('edit-map-data', 'data', allow_duplicate=True)],
#     [Input('btn-minus-edge', 'n_clicks')],
#     [State('edit-edge', 'value'),
#      State('my-mental-health-map', 'elements'),
#      State('edit-map-data', 'data')],
#      prevent_initial_call=True
# )
# def delete_edge_output(n_clicks, edge, elements, edit_map_data):
#     if n_clicks and edge and len(edge) == 2:
#         source = edge[0]
#         target = edge[1]
#         existing_edges = set(edit_map_data['edges'])
#         delete_edge(source, target, elements, existing_edges)
#         edit_map_data['edges'] = list(existing_edges)
#         edit_map_data['elements'] = elements
#     return elements, edit_map_data

@app.callback(
    [Output('my-mental-health-map', 'elements', allow_duplicate=True),
     Output('edit-map-data', 'data', allow_duplicate=True)],
    [Input('btn-minus-edge', 'n_clicks')],
    [State('edit-edge', 'value'),
     State('my-mental-health-map', 'elements'),
     State('edit-map-data', 'data')],
     prevent_initial_call=True
)
def delete_edge_output(n_clicks, edge, elements, edit_map_data):
    if n_clicks and edge and len(edge) == 2:
        source, target = edge

        # Assuming existing_edges is a set of tuples (source, target)
        existing_edges = set([(e['data']['source'], e['data']['target']) for e in elements if 'source' in e.get('data', {})])

        delete_edge(source, target, elements, existing_edges)

        edit_map_data['edges'] = list(existing_edges)
        edit_map_data['elements'] = elements

    return elements, edit_map_data

# Callback: Listens to color scheme user input 
@app.callback(
    [Output('my-mental-health-map', 'stylesheet', allow_duplicate=True),
     Output('edit-map-data', 'data', allow_duplicate=True)],
    [Input('color-scheme', 'value')],
    [State('my-mental-health-map', 'elements'),
     State('edit-map-data', 'data'),
     State('severity-scores', 'data')],
     prevent_initial_call=True
)
def set_color_scheme(selected_scheme, stylesheet, edit_map_data, severity_scores):
    # Update the color scheme based on the selected option
    if selected_scheme is not None and edit_map_data is not None and severity_scores is not None:
        edit_map_data = color_scheme(selected_scheme, edit_map_data, severity_scores)

    # Update elements with the new stylesheet
    stylesheet = edit_map_data['stylesheet']

    return stylesheet, edit_map_data

# Callback: Listens to node sizing user input 
@app.callback(
    [Output('my-mental-health-map', 'stylesheet', allow_duplicate=True),
     Output('edit-map-data', 'data', allow_duplicate=True)],
    [Input('sizing-scheme', 'value')],
    [State('my-mental-health-map', 'elements'),
     State('edit-map-data', 'data'),
     State('severity-scores', 'data')],
    prevent_initial_call=True
)
def set_node_sizes(selected_scheme, stylesheet, edit_map_data, severity_scores):
    if selected_scheme is not None and edit_map_data is not None and severity_scores is not None:
        edit_map_data = node_sizing(chosen_scheme=selected_scheme, graph_data=edit_map_data, severity_scores=severity_scores)

        # Update elements with the new stylesheet
        if 'stylesheet' in edit_map_data:
            stylesheet = edit_map_data['stylesheet']
        else:
            stylesheet = []  # or some default stylesheet

        return stylesheet, edit_map_data
    else:
        return dash.no_update

# Callback: Dynamically generate Likert scales
@app.callback(
    Output('likert-scales-container', 'children'),
    [Input({'type': 'dynamic-dropdown', 'step': 1}, 'value'),
    Input('severity-scores', 'data')]
)
def update_likert_scales(selected_factors, severity_scores):
    if severity_scores is None:
        severity_scores = {}

    if selected_factors is None:
        return []

    return [create_likert_scale(factor, severity_scores.get(factor, 0)) for factor in selected_factors]

# Callback: Update severity scores
# @app.callback(
#     Output('severity-scores', 'data'),
#     [Input({'type': 'likert-scale', 'factor': ALL}, 'value')],
#     State('session-data', 'data')
# )
# def update_severity_scores(severity_values, session_data):
#     severity_scores = {}
#     factors = session_data['dropdowns']['initial-selection']['value']
#     if factors and len(severity_values) != 0:
#         severity_scores = {factor: value for factor, value in zip(factors, severity_values)}
#     else:
#         return dash.no_update
#     return severity_scores

# Callback: Update severity scores
# @app.callback(
#     Output('severity-scores', 'data'),
#     [Input({'type': 'likert-scale', 'factor': ALL}, 'value')],
#     [State('session-data', 'data'),
#      State('severity-scores', 'data')]
# )
# def update_severity_scores(severity_values, session_data, existing_severity_scores):
#     # Initialize severity scores if not present
#     if existing_severity_scores is None:
#         existing_severity_scores = {}

#     # Get the current list of factors
#     current_factors = session_data['dropdowns']['initial-selection']['value']

#     # Update the existing severity scores with new values
#     for factor, value in zip(current_factors, severity_values):
#         existing_severity_scores[factor] = value

#     # Remove severity scores for factors that are no longer present
#     factors_to_remove = set(existing_severity_scores.keys()) - set(current_factors)
#     for factor in factors_to_remove:
#         existing_severity_scores.pop(factor, None)

#     return existing_severity_scores

@app.callback(
    Output('severity-scores', 'data'),
    [Input({'type': 'likert-scale', 'factor': ALL}, 'value')],
    [State('session-data', 'data'),
     State('severity-scores', 'data')]
)
def update_severity_scores(severity_values, session_data, existing_severity_scores):
    # Check if severity_values, session_data or existing_severity_scores is None
    if severity_values is None or session_data is None or existing_severity_scores is None:
        return dash.no_update

    # Initialize severity scores if not present
    if existing_severity_scores is None:
        existing_severity_scores = {}

    # Get the current list of factors
    current_factors = session_data['dropdowns']['initial-selection']['value']

    # Ensure current_factors is not None
    if current_factors is None:
        return dash.no_update

    # Update the existing severity scores with new values
    for factor, value in zip(current_factors, severity_values):
        existing_severity_scores[factor] = value

    # Remove severity scores for factors that are no longer present
    # factors_to_remove = set(existing_severity_scores.keys()) - set(current_factors)
    # for factor in factors_to_remove:
    #     existing_severity_scores.pop(factor, None)

    return existing_severity_scores

# Callback: Update color_scheme dropdown value
@app.callback(
    Output('color_scheme', 'data'),
    Input('color-scheme', 'value')
)
def update_color_scheme_dropdown(value):
    return value

# Callback: Update sizing_scheme dropdown value
@app.callback(
    Output('sizing_scheme', 'data'),
    Input('sizing-scheme', 'value')
)
def update_sizing_scheme_dropdown(value):
    return value

# Callback: Inspect node (highlight direct effects) upon clicking
@app.callback(
    Output('my-mental-health-map', 'stylesheet'),
    [Input('my-mental-health-map', 'tapNodeData'),
     Input('inspect-switch', 'value')],
    State('edit-map-data', 'data')
)
def update_stylesheet(tapNodeData, switch, edit_map_data):
    default_stylesheet = edit_map_data['stylesheet']
    elements = edit_map_data['elements']

    # Reset to default if in view mode
    if 0 not in switch:
        return default_stylesheet

    # If in inspect mode and a node is clicked
    if 0 in switch and tapNodeData:
        clicked_node_id = tapNodeData['id']
        # Find outgoing edges from the clicked node
        outgoing_edges = [e for e in elements if e.get('data', {}).get('source') == clicked_node_id]
        # Find target nodes of these edges
        target_node_ids = {e['data']['target'] for e in outgoing_edges}

        # Adjust the stylesheet for highlighting
        new_stylesheet = []
        for style in default_stylesheet:
            selector = style.get('selector')
            if 'node' in selector or 'edge' in selector:
                # Reduce opacity for all nodes and edges initially
                style['style']['opacity'] = '0.2'
                new_stylesheet.append(style)

        # Highlight the clicked node, its outgoing edges, and target nodes
        new_stylesheet.extend([
            {'selector': f'node[id = "{clicked_node_id}"]', 'style': {'opacity': '1'}},
            {'selector': ','.join([f'node[id = "{n_id}"]' for n_id in target_node_ids]), 'style': {'opacity': '1'}},
            {'selector': ','.join([f'edge[source = "{clicked_node_id}"][target = "{e["data"]["target"]}"]' for e in outgoing_edges]), 'style': {'opacity': '1'}}
        ])

        return new_stylesheet
    # Return default if no node is clicked or if mode is not 'inspect'
    return default_stylesheet

# Information
@app.callback(
    Output('modal-inspect', 'is_open'),
    [Input('help-inspect', 'n_clicks')],
    [State('modal-inspect', 'is_open')],
)
def inspect_info(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output('modal-color-scheme', 'is_open'),
    [Input('help-color', 'n_clicks')],
    [State('modal-color-scheme', 'is_open')],
)
def toggle_modal_color(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output('modal-color-scheme-body', 'children'),
    [Input('color-scheme', 'value')]
)
def update_modal_content_color(selected_scheme):
    if selected_scheme == 'Uniform':
        return 'All the factors in your map have the same color.'
    if selected_scheme == 'Severity':
        return 'The factors in your map are colored based on their relative severity. The darkest factor has the highest indicated severity and the lightest factor has lowest indicated severity.'
    elif selected_scheme == 'Severity (abs)':
        return 'The factors in your map are colored based on their absolute severity. The darkest factor has the highest possible severity score (10) and the lightest factor has the lowest possible severity score (0).'
    elif selected_scheme == 'Out-degree':
        return 'The factors in your map are colored based on their out-degree, which refers to the number of out-going connections. The darkest factor has the most out-going connections and the lightest factor has the least out-going connections. Factors with a lot of out-going connections can be seen as main causes in your map.'
    elif selected_scheme == 'In-degree':
        return 'The factors in your map are colored based on their in-degree, which refers to the number of incoming connections. The darkest factor has the most incoming connections and the lightest factor has the least incoming connections. Factors with a lot of incoming connections can be seen as main effects in your map.'
    elif selected_scheme == 'Out-/In-degree ratio':
        return 'The factors in your map are colored based on their out-/in-degree ratio, which is calculated by dividing the number of out-going by the number of incoming connections. The darkest factor has many out-going and few incoming connections (active), and the lightest factor has few out-going and many incoming connections (passive).'
    return 'As a default the factors in your map are uniformly colored.'

@app.callback(
    Output('modal-sizing-scheme', 'is_open'),
    [Input('help-size', 'n_clicks')],
    [State('modal-sizing-scheme', 'is_open')],
)
def toggle_modal_sizing(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output('modal-sizing-scheme-body', 'children'),
    [Input('sizing-scheme', 'value')]
)
def update_modal_content_sizing(selected_scheme):
    if selected_scheme == 'Uniform':
        return 'All factors in your map have the same size.'
    if selected_scheme == 'Severity':
        return 'The size of the factors in your map corresponds to their relative severity. The largest factor has the highest indicated severity and the smallest factor has lowest indicated severity.'
    elif selected_scheme == 'Severity (abs)':
        return 'The size of the factors in your map corresponds to their absolute severity. The largest factor has the highest possible severity score (10) and the smallest factor has the lowest possible severity score (0).'
    elif selected_scheme == 'Out-degree':
        return 'The size of the factors in your map corresponds to their out-degree, which refers to the number of out-going connections. The largest factor has the most out-going connections and the smallest factor has the least out-going connections. Factors with a lot of out-going connections can be seen as main causes in your map.'
    elif selected_scheme == 'In-degree':
        return 'The size of the factors in your map corresponds to their in-degree, which refers to the number of incoming connections. The largest factor has the most incoming connections and the smallest factor has the least incoming connections. Factors with a lot of incoming connections can be seen as main effects in your map.'
    elif selected_scheme == 'Out-/In-degree ratio':
        return 'The size of the factors in your map corresponds to their out-/in-degree ratio, which is calculated by dividing the number of out-going by the number of incoming connections. The largest factor has many out-going and few incoming connections (active), and the smallest factor has few out-going and many incoming connections (passive).'
    return 'As a default the size of the factors in your map corresponds to their relative severity. The largest factor has the highest indicated severity and the smallest factor has lowest indicated severity.'

# INLCUDE MAP IN HOME TAB (**)
# PROGRESS BAR
# Callback: Download network as image ***
# edges gone ***

if __name__ == '__main__':
    app.run_server(debug=True, port=8069)