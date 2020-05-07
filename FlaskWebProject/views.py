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

salesorder.upload
    js get old itemnubmer + quantity if exists and subtract from GPQuantity
    js check for changes to quantity add new/ subtract old (probably replaces the add/subtract for getpalletdetails
    
data / sql
    clean code to setup in new database
    
testing:
    everything, especially sales order

'''

@app.route('/')
@app.route('/home')
def home():
    username = currentuser.ip_users[request.remote_addr]['username']
    return render_template('index.html', username=username)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/vnd.microsoft.icon')
