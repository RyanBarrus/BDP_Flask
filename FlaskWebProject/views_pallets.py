from FlaskWebProject.globals import *
from flask import render_template, request, flash
from FlaskWebProject import app
import pandas as pd
from datetime import datetime


@app.route('/pallets/upload', methods=['GET', 'POST'])
def palletsUpload():
    if request.method == 'POST':
        ItemNumber = str(request.form['ItemNumber'])
        Pallet = str(request.form['PalletNumber'])
        Timestamp = str(datetime.now())
        UploadUsername = currentuser.username
        CaseBarcodes = [x for x in request.form.getlist('cases') if x != '']
        CaseCount = len(CaseBarcodes)

        df = pd.DataFrame(
            {'ItemNumber': [ItemNumber] * CaseCount,
             'CaseBarcode': CaseBarcodes,
             'Pallet': [Pallet] * CaseCount,
             'Timestamp': [Timestamp] * CaseCount,
             'UploadUsername': [UploadUsername] * CaseCount
            }
        )

        df.to_sql(name='pallets',
                  con=bdp_sqlserver.alchemy_engine(),
                  schema="data",
                  if_exists="append",
                  method="multi",
                  index=False)

        flash('Upload successful', 'success')

    cases = [x for x in range(1, 31)]
    ItemList = bdp_sqlserver.get_rows("SELECT [ItemNumber] FROM [validation].[PalletItemList]")
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('pallets.upload.html', ItemList=ItemList, cases=cases, username=username))


@app.route('/pallets/stirrer', methods=['GET', 'POST'])
def palletsStirrer():
    if request.method == 'POST':
        flash('Not yet implemeneted', "error")

    ItemList = bdp_sqlserver.get_rows("SELECT [ItemNumber] FROM [validation].[StirrerItemList]")
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('pallets.stirrer.html', ItemList=ItemList, username=username))


@app.route('/pallets/delete', methods=['GET', 'POST'])
def palletsDelete():
    palletDatas = None
    if request.method == 'POST':
        if request.form['submit_button'] == "View":
            query = "SELECT * FROM [data].[pallets] WHERE Pallet = ?"
            parameters = request.form['Pallet']
            palletDatas = bdp_sqlserver.get_rows(query, parameters)
        if request.form['submit_button'] == "Delete":
            pallet = request.form['Pallet']
            palletDatas = None
            query = "DELETE FROM [data].[pallets] WHERE PALLET = ?"
            parameters = pallet
            bdp_sqlserver.sql_execute(query, parameters)
            flash('Successfully deleted pallett: ' + pallet, 'success')

    pallets = bdp_sqlserver.get_rows("SELECT Pallet FROM [data].[ViewPallets] ORDER BY Timestamp desc")
    return (render_template('pallets.delete.html', pallets=pallets, palletDatas=palletDatas, username=username))