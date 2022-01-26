import os
from flask import Blueprint, Markup, render_template


# Define the Blueprint object
home_blueprint = Blueprint('home', 'app')

# Set the Blueprint's route and methods
@home_blueprint.route('/home', methods=['GET', ])
def home():
    heading = 'Home'
    description = (
        'Welcome to your flask website!<br></br>'
        'To help you get started, examples have been linked below.'
    )
    desc_html = Markup(description)
    return render_template('home.html', heading=heading, description=desc_html)
