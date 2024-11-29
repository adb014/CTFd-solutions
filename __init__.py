""" Plugin entry-point """

import json
import os
import re

from CTFd.config import process_boolean_str
from CTFd.plugins import override_template
from CTFd.utils import get_app_config

from .blueprint import load_bp
from .models import Solutions

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))

def update_challenge_template(app):
    environment = app.jinja_environment
    PLUGIN_PATH = os.path.dirname(__file__)
    original = app.jinja_loader.get_source(environment, 'challenge.html')[0]
    match = re.search('{% block solves %}', original)
    if match:
        pos = match.start()
        injecting_file_path = os.path.join(PLUGIN_PATH, 'templates/solution_tabpanel.html')
        with open(injecting_file_path, 'r') as f:
            injecting = f.read()
        original = original[:pos] + injecting + original[pos:]

    match = re.search('<div role="tabpanel" class="tab-pane fade" id="solves">', original)
    if match:
        pos = match.start()
        injecting_file_path = os.path.join(PLUGIN_PATH, 'templates/solution_tab.html')
        with open(injecting_file_path, 'r') as f:
            injecting = f.read()
        original = original[:pos] + injecting + original[pos:]
    override_template('challenge.html', original)

    original = app.jinja_loader.get_source(environment, 'challenges.html')[0]
    match = re.search('{% block scripts %}', original)
    if match:
        pos = match.start()
        injecting_file_path = os.path.join(PLUGIN_PATH, 'templates/solution_script.html')
        with open(injecting_file_path, 'r') as f:
            injecting = f.read()
        original = original[:pos+19] + injecting + original[pos+19:]

    override_template('challenges.html', original)


def load(app):
    # Create database tables
    app.db.create_all()

    # Update /challenge/<id> template to include the ability to include
    # solution text
    update_challenge_template(app)

    # Register the blueprint containing the routes
    bp = load_bp()
    app.register_blueprint(bp)

