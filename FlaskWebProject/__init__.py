"""
The flask application package.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


csrf = CSRFProtect(app)

import FlaskWebProject.views
