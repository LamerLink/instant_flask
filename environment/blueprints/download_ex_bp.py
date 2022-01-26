import os
from flask import Blueprint, Markup, render_template, request
from functions import ExportFile


# Define the Blueprint object
download_example_blueprint = Blueprint('download_example', 'app')

# Set the Blueprint's route, arguments, and methods
@download_example_blueprint.route('/download-example', defaults={'file_format': None})
@download_example_blueprint.route('/download-example/<file_format>', methods=['GET', ])
# The arguments in the function need to share the route arguments
def download_example(file_format):
    # Example data, formatted the same way as sqlite3/pyodbc fetchall
    data = [
        ('County', 'Sovereignized', 'Last Ruled', 'Ruled By'),
        ('Egypt', '3150 BC', '1922 AD', 'United Kingdom'),
        ('China', '1600 BC', '1945 AD', 'Japan'),
        ('India', '1500 BC', '1947 AD', 'United Kingdom'),
        ('Japan', '400 AD', '1952', 'Allied Occupation'),
        ('France', '481 AD', '1944', 'Germany'),
        ('United States', '1776 AD', '1781', 'Great Britain'),
    ]
    heading = 'Download Example'
    description = ('Click below to download this table as csv or xlsx.')
    desc_html = Markup(description)
    if file_format == 'csv':
        file = ExportFile(data).to_csv()
    elif file_format == 'xlsx':
        file = ExportFile(data).to_excel()
    else:
        file = None
    return render_template(
        'download_example.html',
        heading=heading,
        file=file,
        result_set=data,
        description=desc_html
    )
