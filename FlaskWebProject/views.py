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

Pallets.stirrer
    post

salesorder.delete
    everything

salesorder.upload
    everything
    
data / sql
    clean code to setup in new database

validation.palletitem create
    switch to lookup from bhprd
    
admin
    add admin functionality

'''


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', currentuser=currentuser)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/vnd.microsoft.icon')


