# Imports
from constants import factors, node_color, node_size
from functions import generate_step_content, create_mental_health_map_tab, create_likert_scale, create_iframe, create_dropdown
from functions import map_add_chains, map_add_cycles, map_add_factors, add_edge, delete_edge, graph_color, color_scheme, node_sizing

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

# # Callback: Display the page & next/back button based on current step 
# @app.callback(
#     [Output('page-content', 'children'),
#      Output('back-button', 'style'),
#      Output('next-button', 'style'),
#      Output('next-button', 'children')],
#     [Input('url', 'pathname'),
#      Input('edit-map-data', 'data'),  # Add this input
#      Input('current-step', 'data')],
#     [State('session-data', 'data'),
#      State('sizing_scheme', 'data')]
# )
# def update_page_and_buttons(pathname, edit_map_data, current_step_data, session_data, sizing):
#     step = current_step_data.get('step', 0)  # Default to step 0 if not found

#     # Default button states
#     content = None
#     back_button_style = hidden_style
#     next_button_style = visible_style
#     next_button_text = "Next"

#     # Update content and button states based on the pathname and step
#     if pathname == '/':
#         content = home_page
#         next_button_style = hidden_style  # Both buttons hidden
#     elif pathname == '/psysys-session':
#         # Check the step and update accordingly
#         if step == 0:
#             content = generate_step_content(step, session_data)
#             next_button_text = "Start"       # Change text to "Start"
#         elif step == 1:
#             content = generate_step_content(step, session_data)
#         elif 2 <= step <= 4:
#             content = generate_step_content(step, session_data)
#             back_button_style = visible_style            # Show back button
#             next_button_style = visible_style            # Show next button
#         elif step == 5:
#             content = generate_step_content(step, session_data)
#             back_button_style = visible_style           # Show back button
#             next_button_text = "Redo"         # Change text to "Redo"

#     elif pathname == "/my-mental-health-map":
#         content = create_mental_health_map_tab(edit_map_data, sizing)
#         back_button_style = hidden_style
#         next_button_style = hidden_style

#     elif content is None:
#         content = html.Div("Page not found")

#     return content, back_button_style, next_button_style, next_button_text
    
# # Callback: Update current step based on next/back button clicks
# @app.callback(
#     Output('current-step', 'data'),
#     [Input('back-button', 'n_clicks'),
#      Input('next-button', 'n_clicks')],
#     [State('current-step', 'data')]
# )
# def update_step(back_clicks, next_clicks, current_step_data):
#     # Initialize click counts to 0 if None
#     back_clicks = back_clicks or 0
#     next_clicks = next_clicks or 0

#     # Use callback_context to determine which input has been triggered
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if "back-button.n_clicks" in changed_id:
#         # Decrement the step, ensuring it doesn't go below 0
#         current_step_data['step'] = max(current_step_data['step'] - 1, 0)
#     elif "next-button.n_clicks" in changed_id:
#         # Increment the step, if it reaches the max step reset to 0
#         if current_step_data['step'] >= 5:
#             current_step_data['step'] = 0
#         else:
#             current_step_data['step'] += 1

#     return current_step_data

# # Callback: Update session data based on user input
# @app.callback(
#     Output('hidden-div', 'children'),
#     Input({'type': 'dynamic-dropdown', 'step': ALL}, 'value')
# )
# def update_hidden_div(values):
#     # Convert values to JSON and return
#     return json.dumps(values)

# # Callback for updating session-data (dropdowns) based on hidden Div
# @app.callback(
#     Output('session-data', 'data'),
#     Input('hidden-div', 'children'),
#     [State('session-data', 'data'),
#      State('current-step', 'data'),
#      State('severity-scores', 'data')]
# )
# def update_session_data(json_values, session_data, current_step_data, severity_scores):

#     step = current_step_data.get('step')
#     values = json.loads(json_values) if json_values else []

#     if len(values) == 1:
#         if step == 1:
#             session_data['dropdowns']['initial-selection']['value'] = values[0]
#             map_add_factors(session_data)
#         elif step == 4:
#             session_data['dropdowns']['target']['value'] = values[0]
#             graph_color(session_data, severity_scores)

#     elif len(values) == 2:
#         if step == 2: 
#             session_data['dropdowns']['chain1']['value'] = values[0]
#             session_data['dropdowns']['chain2']['value'] = values[1]
#             map_add_chains(session_data)
#         elif step == 3: 
#             session_data['dropdowns']['cycle1']['value'] = values[0]
#             session_data['dropdowns']['cycle2']['value'] = values[1]
#             map_add_cycles(session_data)

#     return session_data

# # Callback: Update session data based on initial factor selection
# @app.callback(
#      Output('session-data', 'data', allow_duplicate=True),
#      Input('factor-dropdown', 'value'),
#      State('session-data', 'data'),
#      prevent_initial_call = True
# )
# def dropdown_step5_init(value, session_data):
#     if session_data['add-node'] == []:
#         session_data['add-node'] = value
#     return session_data

# # Callback: Update session data based on current step (reset if 0)
# @app.callback(
#     [Output('session-data', 'data', allow_duplicate=True)],
#     Input('current-step', 'data'),
#     prevent_initial_call=True
# )
# def reset(current_step_data):
#     if current_step_data['step'] == 0:
#         data = {
#             'dropdowns': {
#                 'initial-selection': {'options': [{'label': factor, 'value': factor} for factor in factors], 'value': None},
#                 'chain1': {'options': [], 'value': None},
#                 'chain2': {'options': [], 'value': None},
#                 'cycle1': {'options': [], 'value': None},
#                 'cycle2': {'options': [], 'value': None},
#                 'target': {'options': [], 'value': None},
#             },
#             'elements': [],
#             'edges': [],
#             'add-nodes': [],
#             'add-edges': [],
#             'stylesheet': stylesheet
#         }
#         return (data,) 

#     else:
#         return (dash.no_update,)  

# # Callback: Set edit-graph to session-data if "Load from session" is pressed
# @app.callback(
#     Output('edit-map-data', 'data'),
#     Input('load-map-btn', 'n_clicks'),
#     State('session-data', 'data')
# )
# def load_session_graph(n_clicks, session_data):
#     if n_clicks:
#         # Clone the session_data into edit_map_data
#         return session_data
#     # Return no update if the button wasn't clicked
#     return dash.no_update      

# # Callback: Download graph as file
# @app.callback(
#     Output('download-link', 'data'),
#     Input('download-file-btn', 'n_clicks'),
#     State('edit-map-data', 'data'),
#     prevent_initial_call=True
# )
# def generate_download(n_clicks, data):
#     if n_clicks:
#         # Convert the dictionary to a JSON string
#         json_string = json.dumps(data)
#         return dcc.send_bytes(json_string.encode('utf-8'), "my_mental_health_map.json")
#     return dash.no_update

# # Callback: Upload existing map file
# @app.callback(
#     Output('edit-map-data', 'data', allow_duplicate=True),
#     Input('upload-data', 'contents'),
#     State('upload-data', 'filename'),
#     prevent_initial_call=True
# )
# def upload_graph(contents, filename):
#     if contents:
#         content_type, content_string = contents.split(',')
#         decoded = base64.b64decode(content_string)
#         # Assuming the file is JSON, adjust the decoding as necessary
#         data = json.loads(decoded.decode('utf-8'))
#         return data
#     return dash.no_update

# # Callback: Download network as image ***

# # Callback: Edit map - add node
# @app.callback(
#     [Output('my-mental-health-map', 'elements'),
#      Output('edit-edge', 'options'),
#      Output('edit-map-data', 'data', allow_duplicate=True)],
#     [Input('btn-plus-node', 'n_clicks')],
#     [State('edit-node', 'value'),
#      State('my-mental-health-map', 'elements'),
#      State('edit-map-data', 'data')],
#      prevent_initial_call = True
# )
# def map_add_node(n_clicks, node_name, elements, edit_map_data): 
#     # Else append new node name to add-node list
#     if n_clicks and node_name:
#         # Ensure the node doesn't already exist
#         if not any(node['data']['id'] == node_name for node in elements):
#             new_node = {
#                 'data': {'id': node_name, 'label': node_name},
#                 'style': {'background-color': 'grey'}
#             }
#             elements.append(new_node)

#     # Extract all node names
#     node_names = [node['data']['id'] for node in elements if 'id' in node['data'] and len(node['data']['id']) < 30]
#     edit_map_data['add-nodes'] = node_names
#     edit_map_data['elements'] = elements

#     return elements, node_names, edit_map_data

# # Callback: Remove existing node from graph
# @app.callback(
#     [Output('my-mental-health-map', 'elements', allow_duplicate=True),
#      Output('edit-edge', 'options', allow_duplicate=True),
#      Output('edit-map-data', 'data', allow_duplicate=True)],
#     [Input('btn-minus-node', 'n_clicks')],
#     [State('edit-node', 'value'),
#      State('my-mental-health-map', 'elements'),
#      State('edit-map-data', 'data')],
#      prevent_initial_call=True
# )
# def delete_node(n_clicks, node_id, elements, edit_map_data):
#     if n_clicks and node_id:
#         # Remove the node
#         elements = [element for element in elements if element['data'].get('id') != node_id]

#         # Remove edges connected to the node
#         elements = [element for element in elements if not (('source' in element['data'] and element['data']['source'] == node_id) or ('target' in element['data'] and element['data']['target'] == node_id))]

#     # Extract all node names
#     node_names = [node['data']['id'] for node in elements if 'id' in node['data'] and len(node['data']['id']) < 30]
#     edit_map_data['add-nodes'] = node_names
#     edit_map_data['elements'] = elements

#     return elements, node_names, edit_map_data

# # Callback: Limit dropdown for edit-edge to 2
# @app.callback(
#     Output('edit-edge', 'value'),
#     Input('edit-edge', 'value')
# )
# def limit_dropdown_edit_edge(edit_edge):
#     if edit_edge and len(edit_edge) > 2:
#         return edit_edge[:2]
#     return edit_edge

# # Callback: Add additional edge to graph
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

# # Callback: Delete existing edge from graph
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

# # Callback: Listens to color scheme user input 
# @app.callback(
#     [Output('my-mental-health-map', 'stylesheet', allow_duplicate=True),
#      Output('edit-map-data', 'data', allow_duplicate=True)],
#     [Input('color-scheme', 'value')],
#     [State('my-mental-health-map', 'elements'),
#      State('edit-map-data', 'data'),
#      State('severity-scores', 'data')],
#      prevent_initial_call=True
# )
# def set_color_scheme(selected_scheme, stylesheet, edit_map_data, severity_scores):
#     # Update the color scheme based on the selected option
#     #print(edit_map_data['elements'])
#     if selected_scheme:
#         edit_map_data = color_scheme(selected_scheme, edit_map_data, severity_scores)

#     # Update elements with the new stylesheet
#     stylesheet = edit_map_data['stylesheet']
#     #print(edit_map_data['stylesheet'])

#     return stylesheet, edit_map_data

# # Callback: Listens to node sizing user input (** not working)
# @app.callback(
#     [Output('my-mental-health-map', 'stylesheet', allow_duplicate=True),
#      Output('edit-map-data', 'data', allow_duplicate=True)],
#     [Input('sizing-scheme', 'value')],
#     [State('my-mental-health-map', 'elements'),
#      State('edit-map-data', 'data'),
#      State('severity-scores', 'data')],
#     prevent_initial_call=True
# )
# def set_node_sizes(selected_scheme, stylesheet, edit_map_data, severity_scores):
#     if selected_scheme and edit_map_data and severity_scores is not None:
#         edit_map_data = node_sizing(type=selected_scheme, graph_data=edit_map_data, severity=severity_scores)

#         # Update elements with the new stylesheet
#         if 'stylesheet' in edit_map_data:
#             stylesheet = edit_map_data['stylesheet']
#         else:
#             stylesheet = []  # or some default stylesheet

#         return stylesheet, edit_map_data
#     else:
#         return dash.no_update

# # Callback: Dynamically generate Likert scales
# @app.callback(
#     Output('likert-scales-container', 'children'),
#     [Input({'type': 'dynamic-dropdown', 'step': 1}, 'value'),
#     Input('severity-scores', 'data')]
# )
# def update_likert_scales(selected_factors, severity_scores):
#     if severity_scores is None:
#         severity_scores = {}

#     if selected_factors is None:
#         return []

#     return [create_likert_scale(factor, severity_scores.get(factor, 0)) for factor in selected_factors]

# # Callback: Update severity scores
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