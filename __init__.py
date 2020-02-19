from flask import (Blueprint, render_template, abort, request, redirect)
from jinja2 import TemplateNotFound
from subscribie.db import get_jamla
from subscribie.auth import login_required

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
    try:
        page_title = request.form['page-title']
    except KeyError:
        return "Error: Page title is required"

    try:
        page_body = request.form['page-body']
    except KeyError:
        return "Error: Page body is required"
    return page_title + page_body
