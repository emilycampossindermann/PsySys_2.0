# Works - non-responsive design 
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

# Define style to initiate components
hidden_style = {'display': 'none'}
visible_style = {'display': 'block'}

# Layout elements
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
        html.Div(id='page-content'),
        button_group
    ],
    md=10,
)

app.layout = dbc.Container([
    dbc.Row([nav_col, content_col]),
    dcc.Store(id='current-step', data={'step': 0}, storage_type='local'),
    dcc.Store(id='session-data', data={
        'dropdowns': {
            'initial-selection': {'options':[{'label': factor, 'value': factor} for factor in factors], 'value': None},
            'chain1': {'options':[], 'value': None},
            'chain2': {'options':[], 'value': None},
            'cycle1': {'options':[], 'value': None},
            'cycle2': {'options':[], 'value': None},
            'target': {'options':[], 'value': None},
            },
    }, storage_type='local')
])

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

# Callback: Display the page & next/back button based on current step 
@app.callback(
    [Output('page-content', 'children'),
     Output('back-button', 'style'),
     Output('next-button', 'style'),
     Output('next-button', 'children')],
    [Input('url', 'pathname'),
     Input('current-step', 'data')]
)
def update_page_and_buttons(pathname, current_step_data):
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
            content = step0_content
            next_button_text = "Start"       # Change text to "Start"
        elif step == 1:
            content = step1_content
        elif 2 <= step <= 4:
            content = globals().get(f'step{step}_content')
            back_button_style = visible_style            # Show back button
            next_button_style = visible_style            # Show next button
        elif step == 5:
            content = step5_content
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
    Output('step2-dropdown1', 'options'),
    [Input('factor-dropdown', 'value')]
)
def test_callback(value):
    print("Callback triggered with value:", value)
    return [{'label': v, 'value': v} for v in value or []]

# @app.callback(
#     [
#         Output('step2-dropdown1', 'options'),
#         Output('step2-dropdown2', 'options'),
#         Output('step3-dropdown1', 'options'),
#         Output('step3-dropdown2', 'options'),
#         Output('step4-dropdown', 'options')
#     ],
#     [Input('factor-dropdown', 'value')]
# )
# def populate_followup_dropdowns(selected_factors):
#     print('drin')
#     # Check if there's any factor selected
#     if not selected_factors:
#         # If nothing is selected, provide empty options
#         return [], [], [], [], []

#     # Generate options based on selected factors
#     options = [{'label': factor, 'value': factor} for factor in selected_factors]

#     # Return the same options for all dropdowns in steps 2-4
#     return options, options, options, options, options

# @app.callback(
#     [Output('session-data', 'data'),
#     Output('step2-dropdown1', 'options')],
#     [Input('factor-dropdown', 'value')],
#      State('session-data', 'data')
# )

# def update_session_data(selected_factors, session_data):
#     session_data['dropdowns']['initial-selection']['value'] = selected_factors
#     session_data['dropdowns']['chain1']['options'] = selected_factors
#     session_data['dropdowns']['chain2']['options'] = selected_factors
#     session_data['dropdowns']['cycle1']['options'] = selected_factors
#     session_data['dropdowns']['cycle2']['options'] = selected_factors
#     session_data['dropdowns']['target']['options'] = selected_factors

#     factors = selected_factors

#     all_options = [{'label': factor, 'value': factor} for factor in factors]

#     print(session_data['dropdowns']['initial-selection']['value'])
#     print(all_options)

#     return session_data, all_options

# @app.callback(
#     Output('session-data', 'data'),
#     [Input('factor-dropdown', 'value'),
#      Input('step2-dropdown1', 'value'),
#      Input('step2-dropdown2', 'value'),
#      Input('step3-dropdown1', 'value'),
#      Input('step3-dropdown2', 'value'),
#      Input('step4-dropdown', 'value')],
#      State('session-data', 'data')
# )

# def update_session_data(selected_factors, chain1, chain2, cycle1, cycle2, target, session_data):
#     session_data['dropdowns']['initial-selection']['value'] = selected_factors

#     session_data['dropdowns']['chain1']['options'] = selected_factors
#     session_data['dropdowns']['chain1']['value'] = chain1

#     session_data['dropdowns']['chain2']['options'] = selected_factors
#     session_data['dropdowns']['chain2']['value'] = chain2

#     session_data['dropdowns']['cycle1']['options'] = selected_factors
#     session_data['dropdowns']['cycle1']['value'] = cycle1

#     session_data['dropdowns']['cycle2']['options'] = selected_factors
#     session_data['dropdowns']['cycle2']['value'] = cycle2

#     session_data['dropdowns']['target']['options'] = selected_factors
#     session_data['dropdowns']['target']['value'] = target

#     print('first')
#     print(session_data['dropdown']['initial-selection']['value'])

#     return session_data

# Callback: Update dropdowns & values based on session data (input session data)
# @app.callback(
#     [Output('step2-dropdown1', 'options'),
#      Output('step2-dropdown2', 'options'),
#      Output('step3-dropdown1', 'options'),
#      Output('step3-dropdown2', 'options'),
#      Output('step4-dropdown', 'options')],
#      Input('factor-dropdown', 'value')
# )

# def update_dropdowns(factors):
#     print('hey')
#     selection = factors
#     print('second')
#     print(selection)
#     all_options = [{'label': factor, 'value': factor} for factor in selection]
    
#     return all_options, all_options, all_options, all_options, all_options

# Callback: Populate with value based on session data (not necessary?)

# Callback: Update n_clicks & session data based on current step (reset if 0)


### NEW
# @app.callback(
#     [Output('step2-dropdown1', 'options'),
#      Output('step2-dropdown2', 'options'),
#      Output('step3-dropdown1', 'options'),
#      Output('step3-dropdown2', 'options'),
#      Output('step4-dropdown', 'options')],
#     [Input('factor-dropdown', 'value'),
#      Input('session-data', 'data')]  # Include session data as input
# )
# def update_step2_dropdown_options(selected_factors, session_data):
#     # Use session data to determine selected factors if available
#     if session_data and 'selected_factors' in session_data:
#         factors = session_data['selected_factors']
#     else:
#         # Fallback to selected_factors input if session data is not available
#         factors = selected_factors

#     all_options = [{'label': factor, 'value': factor} for factor in factors]
#     return all_options, all_options, all_options, all_options, all_options



# Callback: Generate mental-health map
# @app.callback(
#     [Output('graph-output', 'elements'),
#      Output('graph-output', 'stylesheet')],
#     [Input('factor-dropdown', 'value'),
#      Input('step2-dropdown1', 'value'),
#      Input('step2-dropdown2', 'value'),
#      Input('step3-dropdown1', 'value'),
#      Input('step3-dropdown2', 'value'),
#      Input('step4-dropdown', 'value')]
# )
# def generate_graph(selected_factors, s2d1, s2d2, s3d1, s3d2, influential_factor):
#     # 1. Convert networkx graph into a dash_cytoscape format
#     elements = []
#     stylesheet = [
#         {
#             'selector': 'node',
#             'style': {
#                 'background-color': 'blue',
#                 'label': 'data(label)'
#             }
#         },
#         {
#             'selector': 'edge',
#             'style': {
#                 'curve-style': 'bezier',
#                 'target-arrow-shape': 'triangle'
#             }
#         }
#     ]

#     for factor in selected_factors:
#         elements.append({'data': {'id': factor, 'label': factor}})

#     existing_edges = set()

#     def add_edge(source, target):
#         edge_key = f"{source}->{target}"  # Create a unique key for the edge
#         if edge_key not in existing_edges:
#             elements.append({'data': {'source': source, 'target': target}})
#             existing_edges.add(edge_key)
    
#     if s2d1 and len(s2d1) == 2:
#         add_edge(s2d1[0], s2d1[1])

#     if s2d2 and len(s2d2) == 2:
#         add_edge(s2d2[0], s2d2[1])

#     if s3d1 and len(s3d1) == 2:
#         add_edge(s3d1[0], s3d1[1])
#         add_edge(s3d1[1], s3d1[0])

#     if s3d2 and len(s3d2) == 3:
#         add_edge(s3d2[0], s3d2[1])
#         add_edge(s3d2[1], s3d2[2])
#         add_edge(s3d2[2], s3d2[0])

#     # Color gradient corresponding to out-degree centrality
#     # 1. Calculate the out-degree centrality
#     out_degrees = {element['data']['id']: 0 for element in elements if 'id' in element['data']}

#     # Then, compute out-degrees for each node
#     for element in elements:
#         if 'source' in element['data']:
#             source = element['data']['source']
#             out_degrees[source] = out_degrees.get(source, 0) + 1

#     # 2. Normalize the out-degree values
#     if out_degrees:  # Check if the list is not empty
#         min_degree = min(out_degrees.values())
#         max_degree = max(out_degrees.values())
#     else:
#         min_degree = 0
#         max_degree = 1

#     def normalize(value):
#         value = float(value)
#         if max_degree - min_degree == 0:
#             return 0.5  
#         return (value - min_degree) / (max_degree - min_degree)


#     normalized_degrees = {node: normalize(degree) for node, degree in out_degrees.items()}

#     # 3. Generate the color gradient
#     def get_color(value):
#         # The blue component remains constant at 255
#         b = 255
#         # Linear interpolation for the red and green components
#         r = int(173 * (1 - value))
#         g = int(216 * (1 - value))
#         return r, g, b
    
#     color_map = {node: get_color(value) for node, value in normalized_degrees.items()}

#     # 4. Update the stylesheet
#     for node, color in color_map.items():
#         r, g, b = color
#         stylesheet.append({
#             'selector': f'node[id="{node}"]',
#             'style': {
#                 'background-color': f'rgb({r},{g},{b})'
#             }
#         })

#     # Add your influential node style
#     if influential_factor:
#         stylesheet.append(
#             {
#                 'selector': f'node[id = "{influential_factor[0]}"]',
#                 'style': {
#                     'border-color': 'red',
#                     'border-width': '2px' 
#                 }
#             }
#         )

#     return elements, stylesheet

if __name__ == '__main__':
    app.run_server(debug=True, port=8001)