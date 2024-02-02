# Imports 
from constants import factors, node_color, node_size
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

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
            dbc.Progress(value=0, striped=True, color="primary", style={"width": "66.5%"}),
            html.Br(),
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
            dbc.Progress(value=0, striped=True, color="primary", style={"width": "66.5%"}),
            html.Br(),
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
            dbc.Progress(value=25, striped=True, color="primary", style={"width": "66.5%"}),
            html.Br(),
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
            dbc.Progress(value=50, striped=True, color="primary", style={"width": "66.5%"}),
            html.Br(),
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
            dbc.Progress(value=75, striped=True, color="primary", style={"width": "66.5%"}),
            html.Br(),
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
            html.Br(), html.Br(), html.Br(),
            html.Div([
                dbc.Progress(value=100, striped=True, color="primary", style={"width": "66.5%", "position": "relative"}),
                html.Span("🎉", style={"font-size": "20px", "margin-left": "10px", "margin-top": "-5px"})
            ], style={"display": "flex"}), 
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
                        style={'width': '90%', 'height': '470px'}
                    )
                ], style={'flex': '1'}),
                ], style={'display': 'flex', 'height': '470px', 'alignItems': 'flex-start', 'marginTop': '28px'}),
                html.Br(),
                ])
    
    else:
        return None

# Function: Create my-mental-health-map editing tab
def create_mental_health_map_tab(edit_map_data, color_scheme_data, sizing_scheme_data):
    # Assuming 'edit_map_data' contains the Cytoscape elements
    cytoscape_elements = edit_map_data.get('elements', [])
    options_1 = [{'label': element['data'].get('label', element['data'].get('id')), 'value': element['data'].get('id')} for element in cytoscape_elements if 'data' in element and 'label' in element['data'] and 'id' in element['data']]
    # options = [{'label': factor, 'value': factor} for factor in factors]
    color_schemes = [{'label': color, 'value': color} for color in node_color]
    sizing_schemes = [{'label': size, 'value': size} for size in node_size]
    return html.Div([
        html.Br(),
        html.Br(),
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

            # Modal for Donation info
            dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Data Donation")),
                       dbc.ModalBody("Here you can anonymously donate your map. Our aim is to continuously improve PsySys to provide scientifically backed content for our users. Therefore, we believe it is imporant to analyze PsySys results to better understand its clinical value and potential use. By choosing to donate your map, you agree that your anonymized data can be used for research purposes.", id = 'donation-info'),
                       dbc.ModalFooter(
                           dbc.Button("Yes, I want to donate", id="donation-agree", className="ms-auto", n_clicks=0))    
                            ],id='donation-modal', is_open=False),

            # Editing features
            html.Div([
                html.Div([
                    dbc.Input(id='edit-node', type='text', placeholder='Enter factor', style={'marginRight': '10px', 'borderRadius': '10px'}),
                    dbc.Button("➕", id='btn-plus-node', color="primary", style={'marginRight': '5px'}),
                    dbc.Button("➖", id='btn-minus-node', color="danger")
                ], style={'display': 'flex', 'alignItems': 'right', 'marginBottom': '10px'}),

                html.Div([
                    dcc.Dropdown(id='edit-edge', options=options_1, placeholder='Enter connection', multi=True, style={'width': '96%', 'borderRadius': '10px'}),
                    dbc.Button("➕", id='btn-plus-edge', color="primary", style={'marginRight': '5px'}),
                    dbc.Button("➖", id='btn-minus-edge', color="danger"),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            
                html.Div([
                    dcc.Dropdown(id='color-scheme', options=color_schemes, value=color_scheme_data, placeholder='Select a color scheme', multi=False, style={'width': '96%', 'borderRadius': '10px'}),
                    dbc.Button("❔", id='help-color', color="light", style={'marginRight': '0px'}),
                    dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Color Scheme Information")),
                               dbc.ModalBody("Content explaining the color scheme will go here...", id='modal-color-scheme-body')
                               ], id="modal-color-scheme"),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),

                html.Div([
                    dcc.Dropdown(id='sizing-scheme', options=sizing_schemes, value=sizing_scheme_data, placeholder='Select a sizing scheme', multi=False, style={'width': '96%', 'borderRadius': '10px'}),
                    dbc.Button("❔", id='help-size', color="light", style={'marginRight': '0px'}),
                    dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Sizing Scheme Information")),
                               dbc.ModalBody("Content explaining the color scheme will go here...", id='modal-sizing-scheme-body')
                               ], id="modal-sizing-scheme", style={"display": "flex", "gap": "5px"}),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                html.Br(),

                html.Div([
                    dbc.Checklist(options=[{"label": "Inspect", "value": 0}],
                                 value=[1],
                                 id="inspect-switch",
                                 switch=True),
                    dbc.Button("❔", id='help-inspect', color="light", style={'marginLeft': '10px'}),
                    dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Inspection Mode")),
                               dbc.ModalBody("Within this mode you can further inspect the consequences of a given factor. Just click on a factor to see its direct effects.", id='modal-inspect-body')
                               ], id="modal-inspect"),
                               ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}), 

            ], style={'width': '300px', 'padding': '10px', 'marginTop': '80px'})
        
        ], style={'display': 'flex', 'height': '470px', 'alignItems': 'flex-start'}),
    ])

# Function: Create tracking tab
def create_tracking_tab(track_data, ):
    return html.Div([
        html.Br(), html.Br(), html.Br(),
        html.Div([cyto.Cytoscape(id='track-graph',
                                 elements=track_data['elements'],
                                 #layout={'name': 'cose', 'fit': True, 'padding': 10},
                                 layout={'name': 'circle'},
                                 zoom=1,
                                 pan={'x': 200, 'y': 200},
                                 stylesheet =track_data['stylesheet'],
                                 style={'width': '90%', 'height': '470px'})
                    ], style={'flex': '1'}),
        
        html.Br(),
    
        dcc.Slider(id='timeline-slider',
                   marks=track_data['timeline-marks'],
                   min=track_data['timeline-min'],
                   max=track_data['timeline-max'],
                   value=track_data['timeline-value'],
                   step=None),

        html.Br(),

        html.Div([
            dcc.Upload(id='upload-graph-tracking', children = dbc.Button("Upload Map", id='upload-map-btn'),
                   style={'display': 'inline-block'}),
            dbc.Button("🗑️", id='delete-tracking-map', color="danger", style={'marginLeft': '10px'}),
                   ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'})
    ])

# Function: Create About us tab
def create_about(app):
    return html.Div([
            html.Br(), html.Br(), html.Br(),
            html.Div([
                html.H2("Making mental-health", style={'fontFamily': 'Courier New', 'marginLeft': '40px', 'fontWeight': 'bold'}),
                html.H2("more graspable", style={'fontFamily': 'Courier New', 'marginLeft': '40px', 'fontWeight': 'bold'}),
                html.H2("for all", style={'fontFamily': 'Courier New', 'marginLeft': '40px', 'fontWeight': 'bold'}),
                html.Br(),
                html.P("With PsySys our goal is to convey the concepts of the network approach to psychopathology directly to users. Thereby, we want to provide users with tools to better understand the dynamics underlying their mental distress. The educational content was created and evaluated within the Psychology Research Master Thesis by Emily Campos Sindermann at the University of Amsterdam (UvA). Since then, we have continued to develop PsySys as a stand-alone application to further investigate its potential clinical utility.", 
                       style={'maxWidth': '900px', 'marginLeft': '40px', 'color':'grey'}),
                html.Hr(style={'maxWidth': '900px', 'marginLeft': '40px'}),
            ]),
            html.Div([
            html.Div([
                html.Div([
                    html.Img(src=app.get_asset_url('DSC_4984.JPG'), style={'width': '160px', 'height': '160px', 'borderRadius': '50%', 'marginRight': '70px', 'marginLeft': '70px'}),
                    html.P("Emily Campos Sindermann", style={'textAlign': 'center', 'marginTop': '10px', 'marginRight': '70px', 'marginLeft': '70px'}),
                    html.P("Research Assistant (MSc)", style={'marginTop': '-15px', 'marginRight': '70px', 'fontStyle': 'italic', 'marginLeft': '70px'}),
                    html.P("Developer", style={'marginTop': '-15px', 'color': 'grey', 'marginRight': '70px', 'fontStyle': 'italic', 'marginLeft': '70px'}),
                ], style={'display': 'inline-block', 'margin': '10px'}),

                html.Div([
                    html.Img(src=app.get_asset_url('profile_dennyborsboom.jpeg'), style={'width': '160px', 'height': '160px', 'borderRadius': '50%', 'marginRight': '90px'}),
                    html.P("Denny Borsboom", style={'textAlign': 'center', 'marginTop': '10px', 'marginRight': '90px'}),
                    html.P("Professor at UvA", style={'marginTop': '-15px', 'marginRight': '90px', 'fontStyle': 'italic'}),
                    html.P("Supervisor", style={'marginTop': '-15px', 'color': 'grey', 'marginRight': '90px', 'fontStyle': 'italic'}),
                ], style={'display': 'inline-block', 'margin': '10px'}),
            ], style={'padding': '20px', 'maxWidth': '900px', 'margin': '0 auto', 'borderRadius': '10px', 'textAlign': 'center'}),

            html.Div([
                html.Div([
                    html.Img(src=app.get_asset_url('profile_tessablanken.jpeg'), style={'width': '160px', 'height': '160px', 'borderRadius': '50%', 'marginRight': '70px'}),
                    html.P("Tessa Blanken", style={'textAlign': 'center', 'marginTop': '10px', 'marginRight': '70px'}),
                    html.P("Assistant Professor at UvA", style={'marginTop': '-15px', 'marginRight': '70px', 'fontStyle': 'italic'}),
                    html.P("Collaborator", style={'marginTop': '-15px', 'color': 'grey', 'marginRight': '70px', 'fontStyle': 'italic'}),
                ], style={'display': 'inline-block', 'margin': '10px'}),

                html.Div([
                    html.Img(src=app.get_asset_url('profile_larsklintwall.jpeg'), style={'width': '160px', 'height': '160px', 'borderRadius': '50%', 'marginRight': '70px'}),
                    html.P("Lars Klintwall", style={'textAlign': 'center', 'marginTop': '10px', 'marginRight': '70px'}),
                    html.P("Professor at Karolinska Institute", style={'marginTop': '-15px', 'marginRight': '70px', 'fontStyle': 'italic'}),
                    html.P("Collaborator", style={'marginTop': '-15px', 'color': 'grey', 'marginRight': '70px', 'fontStyle': 'italic'}),
                ], style={'display': 'inline-block', 'margin': '10px'}),

                html.Div([
                    html.Img(src=app.get_asset_url('profile_julianburger.jpeg'), style={'width': '160px', 'height': '160px', 'borderRadius': '50%'}),
                    html.P("Julian Burger", style={'textAlign': 'center', 'marginTop': '10px'}),
                    html.P("Postdoctorial Researcher at Yale", style={'marginTop': '-15px', 'fontStyle': 'italic'}),
                    html.P("Collaborator", style={'marginTop': '-15px', 'color': 'grey', 'fontStyle': 'italic'}),
                ], style={'display': 'inline-block', 'margin': '10px'}),
            ], style={'padding': '20px', 'maxWidth': '900px', 'margin': '0 auto', 'borderRadius': '10px', 'textAlign': 'center'}),

            ])
            ])


# Function: Initiate graph with elements
def map_add_factors(session_data, value, severity_score):
    if value is None:
        value = []

    current_selection = value
    previous_selection = session_data['dropdowns']['initial-selection']['value'] or []

    # Initialize or clear elements list
    session_data['elements'] = []

    if current_selection:
        # Add factor nodes
        for factor in current_selection:
            session_data['elements'].append({'data': {'id': factor, 'label': factor}})

        # Identify factors that are no longer selected
        removed_factors = [factor for factor in previous_selection if factor not in current_selection]

        # Remove these factors from severity data (dictionary)
        for factor in removed_factors:
            if factor in severity_score:
                del severity_score[factor]

        # Update the edges
        if 'edges' in session_data:
            updated_edges = []
            for edge in session_data['edges']:
                source, target = edge.split('->')
                if source in current_selection and target in current_selection:
                    updated_edges.append(edge)
                    # Adding edge elements
                    session_data['elements'].append({'data': {'source': source, 'target': target, 'id': edge}})
            session_data['edges'] = updated_edges

    # Update the previous selection
    session_data['dropdowns']['initial-selection']['value'] = current_selection

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
    # Remove the edge from elements
    elements[:] = [element for element in elements if not ('source' in element.get('data', {}) and element['data']['source'] == source and 'target' in element.get('data', {}) and element['data']['target'] == target)]
    
    # Remove the edge from existing_edges if it's stored as a tuple (source, target)
    existing_edges.discard((source, target))

# Function: Check if a factor exists in elements
def factor_exists(factor, elements):
    return any(element.get('data', {}).get('id') == factor for element in elements)

# Function: Remove chain edges    
def remove_chain_edges(chain, elements, existing_edges, cycles):
    cycle_edges = set()
    for cycle in cycles:
        for i in range(len(cycle) - 1):
            cycle_edges.add((cycle[i], cycle[i + 1]))

    for i in range(len(chain) - 1):
        edge = (chain[i], chain[i + 1])
        # Only remove edge if it's not in any of the cycles
        if edge not in cycle_edges:
            elements[:] = [e for e in elements if not ('source' in e.get('data', {}) and e['data']['source'] == edge[0] and 'target' in e.get('data', {}) and e['data']['target'] == edge[1])]
            existing_edges[:] = [e for e in existing_edges if not ('source' in e.get('data', {}) and e['data']['source'] == edge[0] and e['data']['target'] == edge[1])]

# Function: Add an edge to the elements
def add_edge_new(source, target, elements):
    edge_data = {'data': {'source': source, 'target': target}}
    if not any(e.get('data') == edge_data['data'] for e in elements):
        elements.append(edge_data)

# Function: Add chain elements
def map_add_chains(session_data, chain1, chain2):
    map_elements = session_data['elements']
    previous_chain1 = session_data['dropdowns']['chain1']['value'] or []
    previous_chain2 = session_data['dropdowns']['chain2']['value'] or []
    cycle1 = session_data['dropdowns']['cycle1']['value'] or []
    cycle2 = session_data['dropdowns']['cycle2']['value'] or []

    existing_edges = session_data['edges']

    # Remove previous selections from elements
    for selection in [previous_chain1, previous_chain2]:
        remove_chain_edges(selection, map_elements, existing_edges, [cycle1, cycle2])

    # Process chain1 and chain2
    for chain in [chain1, chain2]:
        if chain is not None:
            for i in range(len(chain) - 1):
                source, target = chain[i], chain[i + 1]
                if factor_exists(source, map_elements) and factor_exists(target, map_elements):
                    add_edge_new(source, target, map_elements)

    session_data['elements'] = map_elements
    session_data['dropdowns']['chain1']['value'] = chain1
    session_data['dropdowns']['chain2']['value'] = chain2
    session_data['edges'] = existing_edges

    return session_data

# Function: Remove cycle edges
def remove_cycle_edges(cycle, elements, existing_edges, chains):
    # Gather all edges from chain1 and chain2
    chain_edges = set()
    for chain in chains:
        if chain:
            for i in range(len(chain) - 1):
                chain_edges.add((chain[i], chain[i + 1]))

    # Remove edges from the cycle if they are not in the chains
    for i in range(len(cycle)):
        source = cycle[i]
        target = cycle[0] if i == len(cycle) - 1 else cycle[i + 1]
        edge = (source, target)

        # Only remove edge if it's not in chain1 or chain2
        if edge not in chain_edges:
            elements[:] = [e for e in elements if not ('source' in e.get('data', {}) and e['data']['source'] == source and 'target' in e.get('data', {}) and e['data']['target'] == target)]
            existing_edges.discard(edge)

# Function: Add cycles
def map_add_cycles(session_data, cycle1, cycle2):
    map_elements = session_data['elements']
    existing_edges = set(session_data['edges'])

    # Get previous cycles
    previous_cycle1 = session_data['dropdowns']['cycle1']['value'] or []
    previous_cycle2 = session_data['dropdowns']['cycle2']['value'] or []

    chain1 = session_data['dropdowns']['chain1']['value'] or []
    chain2 = session_data['dropdowns']['chain2']['value'] or []

    # Remove previous cycles
    for cycle in [previous_cycle1, previous_cycle2]:
        #remove_cycle_edges(cycle, map_elements, existing_edges)
        remove_cycle_edges(cycle, map_elements, existing_edges, [chain1, chain2])

    # Add new cycles
    for cycle in [cycle1, cycle2]:
        if cycle is not None:
            if len(cycle) == 1:
                element = cycle[0]
                if factor_exists(element, map_elements):
                    add_edge_new(element, element, map_elements)
            elif len(cycle) > 1:
                for i in range(len(cycle)):
                    source = cycle[i]
                    target = cycle[0] if i == len(cycle) - 1 else cycle[i + 1]
                    if factor_exists(source, map_elements) and factor_exists(target, map_elements):
                        add_edge_new(source, target, map_elements)

    session_data['elements'] = map_elements
    session_data['edges'] = list(existing_edges)
    session_data['dropdowns']['cycle1']['value'] = cycle1
    session_data['dropdowns']['cycle2']['value'] = cycle2
    
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
            normalized_degree = 0.5 

        r, g, b = get_color(normalized_degree) 

        degree_style = {
            'selector': f'node[id="{node_id}"]',
            'style': {
                'background-color': f'rgb({r},{g},{b})'
            }
        }
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

# Function: Reset target color
def reset_target(graph_data):
    stylesheet = graph_data['stylesheet']
    new_stylesheet = [style for style in stylesheet 
                      if not (style.get('style', {}).get('border-color') == 'red')]
    graph_data['stylesheet'] = new_stylesheet
    return graph_data

# Function: Color graph (out-degree centrality, target node)
def graph_color(session_data, severity_scores):

    session_data = reset_target(session_data)
    session_data = color_target(session_data)

    session_data = node_sizing(chosen_scheme="Severity", graph_data=session_data, severity_scores=severity_scores)

    return session_data

# Function: Updates edge styles based on strength
def update_edge_opacity(edge_id, strength, stylesheet):
    opacity = strength / 5  # Adjust opacity based on strength
    tapped_edge_style = {
        'selector': f'edge[id="{edge_id}"]',
        'style': {'opacity': opacity}
    }
    # Create a new stylesheet with updated style for the edge
    new_stylesheet = [rule for rule in stylesheet if rule['selector'] != f'edge[id="{edge_id}"]']
    new_stylesheet.append(tapped_edge_style)
    return new_stylesheet
