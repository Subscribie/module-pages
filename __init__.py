from flask import (Blueprint, render_template, abort, request, redirect)
from jinja2 import TemplateNotFound
from subscribie.db import get_jamla
from subscribie.auth import login_required

module_pages = Blueprint('module_pages', __name__, template_folder='templates')

@module_pages.route('/module_pages/index') # Module index page
@login_required
def get_module_pages_index():
    """Return module_pages index page"""

    return "TODO"
