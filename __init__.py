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

@module_pages.route('/delete-pages')
@login_required
def delete_pages_list():
    jamla = get_jamla()
    pages = jamla['pages']

    return render_template('delete_pages_list.html', pages=pages, jamla=get_jamla())

@module_pages.route('/delete-page/<path>', methods=['POST', 'GET'])
@login_required
def delete_page_by_path(path):
    """Delete a given page"""
    jamla = get_jamla()
    if "confirm" in request.args:
        confirm = False
        return render_template(
            "delete_pages_list.html",
            jamla=jamla,
            path=path,
            confirm=False,
        )
    # Perform template file deletion
    templateFile = path + '.html'
    templateFilePath = Path(str(current_app.config['THEME_PATH']), templateFile)
    try:
        templateFilePath.unlink()
    except FileNotFoundError:
        pass

    # Perform jamla page object deletion
    index = 0
    for page in jamla['pages']:
        try:
            page[path]
            jamla['pages'].pop(index)
        except KeyError:
            pass
        index += 1
    # Save updated jamla
    with open(current_app.config["JAMLA_PATH"], "w") as fh:
        yaml.safe_dump(jamla, fh, default_flow_style=False)

    flash('Page deleted.')
    return render_template('delete_pages_list.html', pages=jamla['pages'], jamla=get_jamla())

@module_pages.route('/edit-pages')
@login_required
def edit_pages_list():
    jamla = get_jamla()
    pages = jamla['pages']
    return render_template('edit_pages_list.html', pages=pages, jamla=get_jamla())

@module_pages.route('/edit-page/<path>', methods=['POST', 'GET'])
@login_required
def edit_page(path):
    """Edit a given page"""
    jamla = get_jamla()
    if request.method == 'GET':
        # Get page file contents
        for pageName in jamla['pages']:
            try:
                template_file = pageName[path]['template_file']
            except KeyError:
                pass
        with open(Path(str(current_app.config['THEME_PATH']), template_file)) as fh:
            rawPageContent = fh.read()
        return render_template('edit_page.html', jamla=jamla, rawPageContent=rawPageContent, pageTitle=path)

    elif request.method == 'POST':
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

        # Detect if page name has been changed
        titleChanged = False
        if path != pageName:
            titleChanged = True
            oldTemplateFile = path + '.html'
            # Rename old template file .old
            oldTemplatePath = Path(str(current_app.config['THEME_PATH']), oldTemplateFile)
            oldTemplatePath.replace(Path(str(current_app.config['THEME_PATH']), oldTemplateFile + '.old'))
        # Writeout new template_file to file
        with open(Path(str(current_app.config['THEME_PATH']), template_file), 'w') as fh:
            fh.write(page_body)

        jamla = get_jamla()
        # Check page doesnt already exist
        pageExists = False
        for page in jamla['pages']:
            try:
                page[pageName]
                pageExists = True
            except KeyError:
                pass

        #Remove reference to old page in jamla->pages if title has changed
        if titleChanged:
            index = 0
            for page in jamla['pages']:
                try:
                    page[path]
                    jamla['pages'].pop(index)
                except KeyError:
                    pass
                index += 1

        # Write out updated jamla file
        if pageExists is False or titleChanged:
            # Build updated path dict
            pathDict = {pageName: {'path': pageName, 'template_file' : template_file}}
            jamla['pages'].append(pathDict)
            with open(current_app.config["JAMLA_PATH"], "w") as fh:
                yaml.safe_dump(jamla, fh, default_flow_style=False)
            flash(Markup('Your page <a href="/{}">{}</a> will be visable after reloading'.format(pageName, pageName)))
        else:
            flash(Markup('Page edited. <a href="/{}">{}</a> '.format(pageName, pageName)))

        # Graceful reload app to load new page
        return redirect(url_for('views.reload_app') + '?next=' + url_for('pages.edit_pages_list'))



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
    # Check page doesnt already exist
    pageExists = False
    for page in jamla['pages']:
        try:
            page[pageName]
            pageExists = True
        except KeyError:
            pass
    if pageExists is False:
        jamla['pages'].append(pathDict)
        with open(current_app.config["JAMLA_PATH"], "w") as fh:
            yaml.safe_dump(jamla, fh, default_flow_style=False)
        flash(Markup('Your new page <a href="/{}">{}</a> will be visable after reloading'.format(pageName, pageName)))
    else:
        flash(Markup('The page <a href="/{}">{}</a> already exists'.format(pageName, pageName)))

    # Graceful reload app to load new page
    return redirect(url_for('views.reload_app') + '?next=' + url_for('pages.edit_pages_list'))
