# Imports 
import dash_bootstrap_components as dbc

# Initialize factor list
factors = ["Loss of interest", "Feeling down", "Stress", "Worry", "Overthinking", "Sleep problems", 
           "Joint pain", "Changes in appetite", "Self-blame", "Trouble concentrating", "Procrastinating", 
           "Breakup", "Problems at work", "Interpersonal problems"]

# Initialize node color schemes
node_color = ["Uniform", "Severity", "Severity (abs)", "Out-degree", "In-degree", "Out-/In-degree ratio"]

# Initialize node sizing schemes
node_size = ["Uniform", "Severity", "Severity (abs)", "Out-degree", "In-degree", "Out-/In-degree ratio"] 

toggle = dbc.Form(
    [
        dbc.RadioItems(
            id="mode-toggle",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[
                {"label": "View", "value": "view"},
                {"label": "Inspect", "value": "inspect"},
                {"label": "Annotate", "value": "annotate"},
            ],
            value="view",
        ),
    ],
    className="radio-group",
)