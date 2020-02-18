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
