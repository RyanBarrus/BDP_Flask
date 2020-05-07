from FlaskWebProject.globals import *
from flask import render_template, request, flash
from FlaskWebProject import app
from formencode import variabledecode
import pandas as pd
from datetime import datetime


@app.route('/salesorder/upload', methods=['GET', 'POST'])
def salesorderUpload():
    username = currentuser.ip_users[request.remote_addr]['username']
    if request.method == 'POST':
        parsed = variabledecode.variable_decode(request.form, dict_char='_')
        SONumber = parsed['Available']
        Pallets = [x['Pallet'] for x in [parsed[str(x)] for x in range(1,10)] if x['Pallet'] != '' and x['Quantity'] != '']
        Quantities = [x['Quantity'] for x in [parsed[str(x)] for x in range(1, 10)] if x['Pallet'] != '' and x['Quantity'] != '']
        Timestamp = str(datetime.now())
        datalen = len(Pallets)

        df = pd.DataFrame(
            {'SalesOrderNumber': [SONumber] * datalen,
             'Pallet': Pallets,
             'Quantity': Quantities,
             'Timestamp': [Timestamp] * datalen,
             'UploadUsername': [username] * datalen
             }
        )

        df.to_sql(name='shipments',
                  con=bdp_sqlserver.alchemy_engine(),
                  schema="data",
                  if_exists="append",
                  method="multi",
                  index=False)

        flash('Upload successful', 'success')



    PalletHolders = [{'Pallet':str(x)+'_Pallet','Quantity':str(x)+'_Quantity','ItemNumber':str(x)+'_ItemNumber'} for x in range(1,10)]
    query = "SELECT SONumber FROM dbo.a_PlasticsPotentialASNOrders ORDER BY Posted, SONumber"
    Availables = bhprd_sqlserver.get_rows(query)
    return (render_template('salesorder.upload.html', Availables=Availables,PalletHolders=PalletHolders, username=username))


@app.route('/salesorder/wrinlist', methods=['GET', 'POST'])
def salesorderWrin():
    ExistingData = {}
    if request.method == 'POST':
        if request.form['submit_button'] == "Add":
            ItemNumber = request.form['Available']
            WRIN = request.form['WRIN']
            GTIN = request.form['GTIN']
            query = "INSERT INTO dbo.a_ITEM_WRIN_MAP (ITEMNMBR,WRIN,GTIN) VALUES (?,?,?)"
            parameters = (ItemNumber,WRIN,GTIN)
            bhprd_sqlserver.sql_execute(query,parameters)
            flash('Successfully added: ' + ItemNumber + ' with WRIN: ' + WRIN + ' and GTIN: ' + GTIN, 'success')
        if request.form['submit_button'] == "View":
            ItemNumber = request.form['Existing']
            query = "SELECT ITEMNMBR AS ItemNumber, RTRIM(WRIN), RTRIM(GTIN) FROM dbo.a_ITEM_WRIN_MAP WHERE ITEMNMBR = ?"
            parameters = (ItemNumber)
            ExistingData = bhprd_sqlserver.get_rows(query, parameters)
            ExistingData = {
                "ItemNumber":ExistingData[0][0],
                "WRIN":ExistingData[0][1],
                "GTIN":ExistingData[0][2]
            }

        if request.form['submit_button'] == "Update":
            ItemNumber = request.form['ExistingItemNumber']
            WRIN = request.form['ExistingWRIN']
            GTIN = request.form['ExistingGTIN']
            query = "UPDATE dbo.a_ITEM_WRIN_MAP SET WRIN = ?, GTIN = ? WHERE ITEMNMBR = ?"
            parameters = (WRIN,GTIN,ItemNumber)
            bhprd_sqlserver.sql_execute(query,parameters)
            flash('Updated ' + ItemNumber + ' to WRIN: ' + WRIN + ' and GTIN: ' + GTIN, 'success')

        if request.form['submit_button'] == "Remove":
            ItemNumber = request.form['ExistingItemNumber']
            query = "DELETE FROM dbo.a_ITEM_WRIN_MAP WHERE ITEMNMBR = ?"
            parameters = (ItemNumber)
            bhprd_sqlserver.sql_execute(query,parameters)
            flash('Removed Itemnumber: ' + ItemNumber, 'success')

    query = "SELECT ITEMNMBR AS ItemNumber FROM dbo.IV00101 WHERE ITEMNMBR NOT IN (SELECT ITEMNMBR FROM dbo.a_ITEM_WRIN_MAP)"
    Availables = bhprd_sqlserver.get_rows(query)
    query = "SELECT ITEMNMBR AS ItemNumber FROM dbo.a_ITEM_WRIN_MAP"
    Existings = bhprd_sqlserver.get_rows(query)
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('salesorder.wrinlist.html', Availables=Availables, Existings=Existings, ExistingData=ExistingData, username=username))

@app.route('/salesorder/dclist', methods=['GET', 'POST'])
def salesorderDC():
    ExistingData = {}
    if request.method == 'POST':
        if request.form['submit_button'] == "Add":
            CustomerNumber = request.form['Available']
            DCID = request.form['DCID']
            GLN = request.form['GLN']
            query = "INSERT INTO dbo.a_DistributionCenters ([Customer Number],[Destination Location ID],[Destination GLN]) VALUES (?,?,?)"
            parameters = (CustomerNumber, DCID, GLN)
            bhprd_sqlserver.sql_execute(query, parameters)
            flash('Successfully added: ' + CustomerNumber + ' with DCID: ' + DCID + ' and GLN: ' + GLN, 'success')
        if request.form['submit_button'] == "View":
            CustomerNumber = request.form['Existing']
            query = "SELECT [Customer Number], RTRIM([Destination Location ID]),RTRIM([Destination GLN]) FROM dbo.a_DistributionCenters WHERE [Customer Number] = ?"
            parameters = (CustomerNumber)
            ExistingData = bhprd_sqlserver.get_rows(query, parameters)
            ExistingData = {
                "CustomerNumber": ExistingData[0][0],
                "DCID": ExistingData[0][1],
                "GLN": ExistingData[0][2]
            }

        if request.form['submit_button'] == "Update":
            CustomerNumber = request.form['ExistingCustomerNumber']
            DCID = request.form['ExistingDCID']
            GLN = request.form['ExistingGLN']
            query = "UPDATE dbo.a_DistributionCenters SET [Destination Location ID] = ?, [Destination GLN] = ? WHERE [Customer Number] = ?"
            parameters = (DCID, GLN, CustomerNumber)
            bhprd_sqlserver.sql_execute(query, parameters)
            flash('Updated ' + CustomerNumber + ' to DCID: ' + DCID + ' and GLN: ' + GLN, 'success')

        if request.form['submit_button'] == "Remove":
            CustomerNumber = request.form['ExistingCustomerNumber']
            query = "DELETE FROM dbo.a_DistributionCenters WHERE [Customer Number] = ?"
            parameters = (CustomerNumber)
            bhprd_sqlserver.sql_execute(query, parameters)
            flash('Removed Customer Number: ' + CustomerNumber, 'success')

    query = "SELECT CUSTNMBR AS CustomerNumber FROM dbo.RM00101 WHERE CUSTNMBR NOT IN (SELECT [Customer Number] FROM dbo.a_DistributionCenters)"
    Availables = bhprd_sqlserver.get_rows(query)
    query = "SELECT [Customer Number] AS CustomerNumber FROM dbo.a_DistributionCenters"
    Existings = bhprd_sqlserver.get_rows(query)
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('salesorder.dclist.html', Availables=Availables, Existings=Existings,
                            ExistingData=ExistingData, username=username))


@app.route('/salesorder/delete', methods=['GET', 'POST'])
def salesorderDelete():
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('salesorder.delete.html', username=username))