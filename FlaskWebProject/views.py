from os import path
from flask import send_from_directory
from FlaskWebProject import app
from FlaskWebProject.globals import *
from FlaskWebProject.views_user import *
from FlaskWebProject.views_pallets import *
from FlaskWebProject.views_salesorder import *
from FlaskWebProject.views_validation import *
from FlaskWebProject.views_fetch import *

'''
Todo:

ftp: 
    finish ftp / sendToHavi funciton
      
data / sql
    clean code to setup in new database
    
testing:
    everything, especially sales order
    
'''

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/vnd.microsoft.icon')
