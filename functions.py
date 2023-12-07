# Imports 
from constants import factors, node_color, node_size, toggle
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import copy

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

# Function: Generate likert scales to indicate factor severity
def create_likert_scale(factor, initial_value=0):
    return html.Div([
        html.Label([
            'Severity of ',
            html.Span(factor, style={'font-weight': 'bold', 'color': 'black'})
        ]),
        dcc.Slider(
            min=0,
            max=10,
            step=1,
            value=initial_value,
            marks={i: str(i) for i in range(11)},
            id={'type': 'likert-scale', 'factor': factor}
        )
    ])

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
            html.Div(id='likert-scales-container'),
            html.Br()
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
                ], style={'display': 'flex', 'height': '470px', 'alignItems': 'flex-start', 'marginTop': '80px'}),
                html.Br(),
                ])
    
    else:
        return None

# Function: Create my-mental-health-map editing tab
def create_mental_health_map_tab(edit_map_data, color_scheme_data, sizing_scheme_data):
    options = [{'label': factor, 'value': factor} for factor in factors]
    color_schemes = [{'label': color, 'value': color} for color in node_color]
    sizing_schemes = [{'label': size, 'value': size} for size in node_size]
    return html.Div([
        html.Br(),
        html.Br(),
        # html.H3("My Mental-Health Map"),
        html.Div([
            html.Div([
                cyto.Cytoscape(
                    id='my-mental-health-map',
                    elements=edit_map_data['elements'],
                    layout={'name': 'cose', 'fit': True, 'padding': 10},
                    zoom=1,
                    pan={'x': 200, 'y': 200},
                    stylesheet=edit_map_data['stylesheet'],
                    style={'width': '90%', 'height': '480px'}
                ),
                html.Br(),
                html.Div([
                    dbc.Button("Load PsySys Map", id='load-map-btn', className="me-2"),
                    # Style the dcc.Upload component to look like a button
                    dcc.Upload(
                        id='upload-data',
                        children=dbc.Button("Upload Map", id='upload-map-btn'),
                        style={
                            'display': 'inline-block',
                        },
                    ),
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'}),
                
                html.Div([
                    dbc.Button("Download as File ", id='download-file-btn'),
                    dbc.Button("Download as Image", id='download-image-btn'),
                    dbc.Button("Donate", id="donate-btn", color="success")
                               #style={'backgroundColor': '#4CBB17', 'border': 'none', 'color':'white'})
                ], style={'display': 'flex', 'marginTop': '10px', 'gap': '10px'})
            ], style={'flex': '1'}),

            # Modal for node name & severity edit
            dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Factor Information")),
                       dbc.ModalBody([
                           html.Div("Name:"),
                           dbc.Input(id='modal-node-name', type='text'),
                           html.Br(),
                           html.Div("Severity Score:"),
                           dcc.Slider(id='modal-severity-score', min=0, max=10, step=1),
                           html.Br(),
                           html.Div("Notes:"),
                           dcc.Textarea(
                               id='note-input',
                               value='',
                               className='custom-textarea',
                               style={
                                   'flex': '1',  # Flex for input to take available space 
                                   'fontSize': '0.9em',  # Adjust font size to make textbox smaller
                                   'resize': 'none',
                                   'width': '32em',
                                   'height': '10em'
                                }
                            )
                           ]),
                        dbc.ModalFooter(
                            dbc.Button("Save Changes", id="modal-save-btn", className="ms-auto", n_clicks=0))    
                            ],
                            id='node-edit-modal',
                            is_open=False),

            # Modal for edge info
            dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Connection Information")),
                       dbc.ModalBody([
                           html.Div(id='edge-explanation'),
                           html.Br(),
                           html.Div("Strength of the relationship:"),
                           dcc.Slider(id='edge-strength', min=1, max=5, step=1),
                           html.Br(),
                           html.Div("Notes:"),
                           dcc.Textarea(
                               id='edge-annotation',
                               value='',
                               className='custom-textarea',
                               style={
                                   'flex': '1',  # Flex for input to take available space 
                                   'fontSize': '0.9em',  # Adjust font size to make textbox smaller
                                   'resize': 'none',
                                   'width': '32em',
                                   'height': '10em'
                                }
                            )
                           ]),
                        dbc.ModalFooter(
                            dbc.Button("Save Changes", id="edge-save-btn", className="ms-auto", n_clicks=0))    
                            ],
                            id='edge-edit-modal',
                            is_open=False),

            # Editing features
            html.Div([
                html.Div([
                    dbc.Input(id='edit-node', type='text', placeholder='Enter factor', style={'marginRight': '10px', 'borderRadius': '10px'}),
                    dbc.Button("➕", id='btn-plus-node', color="primary", style={'marginRight': '5px'}),
                    dbc.Button("➖", id='btn-minus-node', color="danger")
                ], style={'display': 'flex', 'alignItems': 'right', 'marginBottom': '10px'}),

                html.Div([
                    dcc.Dropdown(id='edit-edge', options=options, placeholder='Enter connection', multi=True, style={'width': '96%', 'borderRadius': '10px'}),
                    dbc.Button("➕", id='btn-plus-edge', color="primary", style={'marginRight': '5px'}),
                    dbc.Button("➖", id='btn-minus-edge', color="danger")
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            
                html.Div([
                    dcc.Dropdown(id='color-scheme', options=color_schemes, value=color_scheme_data, placeholder='Select a color scheme', multi=False, style={'width': '96%', 'borderRadius': '10px'}),
                    dbc.Button("❔", id='help-color', color="light", style={'marginRight': '0px'}),
                    dbc.Modal([dbc.ModalHeader("Color Scheme Information"),
                               dbc.ModalBody("Content explaining the color scheme will go here...", id='modal-color-scheme-body')
                               ], id="modal-color-scheme"),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

                html.Div([
                    dcc.Dropdown(id='sizing-scheme', options=sizing_schemes, value=sizing_scheme_data, placeholder='Select a sizing scheme', multi=False, style={'width': '96%', 'borderRadius': '10px'}),
                    dbc.Button("❔", id='help-size', color="light", style={'marginRight': '0px'}),
                    dbc.Modal([dbc.ModalHeader("Node Size Information"),
                               dbc.ModalBody("Content explaining the color scheme will go here...", id='modal-sizing-scheme-body')
                               ], id="modal-sizing-scheme", style={"display": "flex", "gap": "5px"}),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

                html.Br(), html.Br(),
                html.Div([toggle]),
                html.Br(), html.Br(),
                html.Div(id='annotation-interface', children=[
                    html.Div(
                    dcc.Textarea(
                        id='annotation-input',
                        value='',
                        className='custom-textarea',
                        style={
                            'display': 'none',
                            'flex': '1',  # Flex for input to take available space
                            'fontSize': '0.9em',  # Adjust font size to make textbox smaller
                            'resize': 'none'
                        }
                    ),
                    style={'flex': '1', 'marginRight': '3px', 
                           'borderRadius': '10px !important'}  # Margin applied to the wrapper div
                ),
                html.Div(
                    dbc.Button('💾', id='save-annotation-btn', style={'display': 'none'}),
                    style={'flex': 'none'}  # This div doesn't grow or shrink
                )
            ], style={
                'display': 'flex', 
                'alignItems': 'center', 
                'marginBottom': '10px'
            })


            #     html.Div(id='annotation-interface', children=[
            #         dcc.Textarea(id='annotation-input',
            #                      value='',
            #                      style={'display': 'none'}),
            #         html.Br(),
            #         dbc.Button('Save', id='save-annotation-btn', 
            #                    style={'display': 'none'})])

            ], style={'width': '300px', 'padding': '10px', 'marginTop': '80px'})
        
        ], style={'display': 'flex', 'height': '470px', 'alignItems': 'flex-start'}),
    ])

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

# Function: Normalize        
def normalize(value, max_degree, min_degree):
    value = float(value)
    if max_degree - min_degree == 0:
        return 0.5  
    return (value - min_degree) / (max_degree - min_degree)

# Function: Color gradient
def get_color(value):
    b = 255
    r = int(173 * (1 - value))
    g = int(216 * (1 - value))
    return r, g, b

# Function: Calculate degree centrality
def calculate_degree_centrality(elements, degrees):
    for element in elements:
        if 'source' in element['data']:
            source = element['data']['source']
            degrees[source]['out'] = degrees[source].get('out', 0) + 1
        if 'target' in element['data']:
            target = element['data']['target']
            degrees[target]['in'] = degrees[target].get('in', 0) + 1
    return elements, degrees

# Function: Apply uniform color
def apply_uniform_color_styles(stylesheet):
    # Define the uniform color style for nodes
    uniform_color_style = {
        'selector': 'node',
        'style': {
            'background-color': 'blue',
            'label': 'data(label)'  # Ensure labels are maintained
        }
    }
    # Remove any existing node color styles
    stylesheet = [style for style in stylesheet if 'background-color' not in style.get('style', {})]
    # Append the uniform color style
    stylesheet.append(uniform_color_style)
    return stylesheet

# Function: Apply severity color
def apply_severity_color_styles(type, stylesheet, severity_scores, default_style):
    # Check if severity_scores is not empty and valid
    if severity_scores and all(isinstance(score, (int, float)) for score in severity_scores.values()):
        if type == "Severity":
            max_severity = max(severity_scores.values())
            min_severity = min(severity_scores.values())
        elif type == "Severity (abs)":
            max_severity = 10
            min_severity = 1

        # Normalize and apply color based on severity
        for node_id, severity in severity_scores.items():
            normalized_severity = (severity - min_severity) / (max_severity - min_severity)
            r, g, b = get_color(normalized_severity)  # Assuming get_color is defined as before

            severity_style = {
                'selector': f'node[id="{node_id}"]',
                'style': {
                    'background-color': f'rgb({r},{g},{b})'
                }
            }
            # Append the style for this node
            stylesheet.append(severity_style)

    elif severity_scores == {}:
        stylesheet = default_style

    return stylesheet

# Function: Apply degree centrality color
def apply_centrality_color_styles(type, stylesheet, elements):
    degrees = {element['data']['id']: {'out': 0, 'in': 0} for element in elements 
               if 'id' in element['data']}
    
    # Calculate in-degree and out-degree
    elements, degrees = calculate_degree_centrality(elements, degrees)

    # Compute centrality based on the selected type
    computed_degrees = {}
    for id, degree_counts in degrees.items():
        if type == "Out-degree":
            computed_degrees[id] = degree_counts['out']
        elif type == "In-degree":
            computed_degrees[id] = degree_counts['in']
        elif type == "Out-/In-degree ratio":
            if degree_counts['in'] != 0:
                computed_degrees[id] = degree_counts['out'] / degree_counts['in']
            else:
                computed_degrees[id] = 0  # or some other default value you deem appropriate
    if computed_degrees:
        min_degree = min(computed_degrees.values())
        max_degree = max(computed_degrees.values())
    else:
        min_degree = 0
        max_degree = 1

    for node_id, degree in computed_degrees.items():
        if max_degree != min_degree:
            # Normalized degree value when max and min degrees are different
            normalized_degree = (degree - min_degree) / (max_degree - min_degree)
        else:
            # Default normalized value when max and min degrees are the same
            normalized_degree = 0.5  # or any default value that suits your application

        r, g, b = get_color(normalized_degree)  # Assuming get_color is defined as before

        degree_style = {
            'selector': f'node[id="{node_id}"]',
            'style': {
                'background-color': f'rgb({r},{g},{b})'
            }
        }
        # Append the style for this node
        stylesheet.append(degree_style)

    return stylesheet

# Function: Set color scheme
def color_scheme(chosen_scheme, graph_data, severity_scores):
    elements = graph_data['elements']
    stylesheet = graph_data['stylesheet']
    default_style = [{'selector': 'node','style': {'background-color': 'blue', 'label': 'data(label)'}},
                     {'selector': 'edge','style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}]
    
    if chosen_scheme == "Uniform":
        graph_data['stylesheet'] = apply_uniform_color_styles(graph_data['stylesheet'])
    elif chosen_scheme in ["Severity", "Severity (abs)"]:
        graph_data['stylesheet'] = apply_severity_color_styles(chosen_scheme, graph_data['stylesheet'], severity_scores, default_style)
    elif chosen_scheme in ["Out-degree", "In-degree", "Out-/In-degree ratio"]:
        graph_data['stylesheet'] = apply_centrality_color_styles(chosen_scheme, graph_data['stylesheet'], elements)
    
    return graph_data

# Function: Normalize size
def normalize_size(value, max_value, min_value, min_size, max_size):
    if max_value == min_value:
        # If max and min values are equal, return the average size to avoid division by zero
        return (max_size + min_size) / 2

    # Normalize the value to a range between min_size and max_size
    normalized = (value - min_value) / (max_value - min_value)
    return normalized * (max_size - min_size) + min_size

# Function: Apply uniform node sizing 
def apply_uniform_size_styles(stylesheet):
    # Define the uniform size style
    uniform_size_style = {
        'selector': 'node',
        'style': {'width': 25, 'height': 25}  # Example sizes
    }
    # Apply this style to the stylesheet
    stylesheet = [style for style in stylesheet if 'width' not in style.get('style', {})]
    stylesheet.append(uniform_size_style)

    return stylesheet

# Function: Apply severity node sizing
def apply_severity_size_styles(type, stylesheet, severity_scores, default_style):
    # Check if severity_scores is not empty and valid
    max_size = 50
    min_size = 10

    #print(severity_scores.items())
    if severity_scores and all(isinstance(score, (int, float)) for score in severity_scores.values()):
        if type == "Severity":
            max_severity = max(severity_scores.values())
            min_severity = min(severity_scores.values())
        elif type == "Severity (abs)":
            max_severity = 10
            min_severity = 1

        # Normalize and apply color based on severity
        for node_id, severity in severity_scores.items():
            size = normalize_size(severity, max_severity, min_severity, min_size, max_size)

            severity_style = {
                'selector': f'node[id="{node_id}"]',
                'style': {'width': size,'height': size}
                }
            
            # Append the style for this node
            stylesheet.append(severity_style)

    elif severity_scores == {}:
        stylesheet = default_style
        #return dash.no_update

    return stylesheet

# Function: Apply degree centraliy node sizing
def apply_centrality_size_styles(type, stylesheet, elements):
    max_size = 50
    min_size = 10

    degrees = {element['data']['id']: {'out': 0, 'in': 0} for element in elements 
               if 'id' in element['data']}
    
    # Calculate in-degree and out-degree
    elements, degrees = calculate_degree_centrality(elements, degrees)

    # Compute centrality based on the selected type
    computed_degrees = {}
    for id, degree_counts in degrees.items():
        if type == "Out-degree":
            computed_degrees[id] = degree_counts['out']
        elif type == "In-degree":
            computed_degrees[id] = degree_counts['in']
        elif type == "Out-/In-degree ratio":
            if degree_counts['in'] != 0:
                computed_degrees[id] = degree_counts['out'] / degree_counts['in']
            else:
                computed_degrees[id] = 0  # or some other default value you deem appropriate

    if computed_degrees:
        min_degree = min(computed_degrees.values())
        max_degree = max(computed_degrees.values())
    else:
        min_degree = 0
        max_degree = 1

    for node_id, degree in computed_degrees.items():
        size = normalize_size(degree, max_degree, min_degree, min_size, max_size)

        degree_style = {
            'selector': f'node[id="{node_id}"]',
            'style': {'width': size, 'height': size}
        }

        # Append the style for this node
        stylesheet.append(degree_style)

    return stylesheet

# Function: Set node sizing scheme 
def node_sizing(chosen_scheme, graph_data, severity_scores):
    elements = graph_data['elements']
    stylesheet = graph_data['stylesheet']
    default_style = [{'selector': 'node','style': {'background-color': 'blue', 'label': 'data(label)'}},
                     {'selector': 'edge','style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}]
    
    if chosen_scheme == "Uniform":
        graph_data['stylesheet'] = apply_uniform_size_styles(graph_data['stylesheet'])
    elif chosen_scheme in ["Severity", "Severity (abs)"]:
        graph_data['stylesheet'] = apply_severity_size_styles(chosen_scheme, graph_data['stylesheet'], severity_scores, default_style)
    elif chosen_scheme in ["Out-degree", "In-degree", "Out-/In-degree ratio"]:
        graph_data['stylesheet'] = apply_centrality_size_styles(chosen_scheme, graph_data['stylesheet'], elements)
    
    return graph_data

# Function: Color most influential fator in graph 
def color_target(graph_data):
    influential_factor = graph_data['dropdowns']['target']['value']
    stylesheet = graph_data['stylesheet']

    if influential_factor:
        stylesheet.append({'selector': f'node[id = "{influential_factor[0]}"]',
                           'style': {'border-color': 'red','border-width': '2px'}})
        
    graph_data['stylesheet'] = stylesheet
    return graph_data

def reset_target(graph_data):
    stylesheet = graph_data['stylesheet']
    new_stylesheet = [style for style in stylesheet 
                      if not (style.get('style', {}).get('border-color') == 'red')]
    graph_data['stylesheet'] = new_stylesheet
    return graph_data

# Function: Color graph (out-degree centrality, target node)
def graph_color(session_data, severity_scores):

    # Add influential node style
    #session_data = color_scheme(type="Severity", graph_data=session_data, severity_scores=severity_scores)
    session_data = reset_target(session_data)
    session_data = color_target(session_data)

    session_data = node_sizing(chosen_scheme="Severity", graph_data=session_data, severity_scores=severity_scores)

    return session_data

# Function: Initialize annotation tooltips
# def initialize_annotations(mode, edit_map_data, annotation_data):
#     if mode == 'annotate':
#         elements = edit_map_data.get('elements', [])
#         for element in elements:
#             if 'id' in element['data']:
#                 node_id = element['data']['id']
#                 annotation = annotation_data.get(node_id, "No annotation")
#                 element['data']['tooltip'] = annotation  # Add tooltip content
#         return elements
#     return dash.no_update

# Function: Update stylesheet with tooltips
# def update_stylesheet_based_on_mode(mode, edit_map_data):
#     default_stylesheet = edit_map_data.get('stylesheet', [])
#     if mode == 'annotate':
#         tooltip_stylesheet = [
#             {
#                 'selector': 'node',
#                 'style': {
#                     'content': 'data(label)'  # Display the node label
#                 }
#             },
#             {
#                 'selector': 'node:hover',
#                 'style': {
#                     'content': 'data(tooltip)',  # Display the tooltip content on hover
#                     'text-valign': 'center',
#                     'text-halign': 'center',
#                     'background-color': '#fff',
#                     'border-color': '#000',
#                     'border-width': '1px',
#                     'border-style': 'solid',
#                     'font-size': '12px',
#                     'padding': '5px',
#                     'z-index': '9999'
#                 }
#             }
#         ]
#         return default_stylesheet + tooltip_stylesheet
#     else:
#         return default_stylesheet