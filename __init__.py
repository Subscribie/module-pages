from flask import (Blueprint, render_template, abort, request, redirect,
        current_app, url_for, flash, Markup)
from jinja2 import TemplateNotFound
from subscribie.db import get_jamla
from subscribie.auth import login_required
from pathlib import Path
import yaml

module_pages = Blueprint('pages', __name__, template_folder='templates')

@module_pages.route('/pages/index') # Module index page
@module_pages.route('/Add-pages')
@login_required
def get_module_pages_index():
    """Return module_pages index page"""

    return render_template('module_pages_index.html', jamla=get_jamla())

@module_pages.route('/add-page')
@login_required
def add_page():
    """Return add page form"""
    return render_template('add_page.html', jamla=get_jamla())

@module_pages.route('/add-page', methods=['POST'])
@login_required
def save_new_page():
    """Save the new page to jamla

        Writes out a new file <page-name>.html
        and updates jamla.yaml with the newly 
        added page.
    """
    try:
        page_title = request.form['page-title']
    except KeyError:
        return "Error: Page title is required"

    try:
        page_body = request.form['page-body']
    except KeyError:
        return "Error: Page body is required"

    # Generate a valid path for url
    pageName = ''
    for char in page_title:
        if char.isalnum():
            pageName += char
    # Generate a valid html filename
    template_file = pageName + '.html'

    # Writeout template_file to file
    with open(Path(str(current_app.config['THEME_PATH']), template_file), 'w') as fh:
        fh.write(page_body)

    # Add path to jamla and save jamla
    pathDict = {pageName: {'path': pageName, 'template_file' : template_file}}
    jamla = get_jamla()
    jamla['pages'].append(pathDict)
    with open(current_app.config["JAMLA_PATH"], "w") as fh:
        yaml.safe_dump(jamla, fh, default_flow_style=False)
    flash(Markup('Your new page <a href="/{}">{}</a> will be visable after reloading'.format(pageName, pageName)))

    # Graceful reload app to load new page
    return redirect(url_for('views.reload_app'))
