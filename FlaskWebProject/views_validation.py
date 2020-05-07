from FlaskWebProject.globals import *
from flask import render_template, request, flash
from FlaskWebProject import app
import pandas as pd


@app.route('/validation/palletitem', methods=['GET', 'POST'])
def validationPalletItem():
    if request.method == 'POST':
        if request.form['submit_button'] == "Add":
            PalletItem = request.form['AddItem']
            query = "INSERT INTO [validation].[PalletItemList] (ItemNumber) VALUES (?)"
            parameters = PalletItem
            bdp_sqlserver.sql_execute(query, parameters)
            flash('Item successfully added: ' + PalletItem, "success")

        if request.form['submit_button'] == "Remove":
            for selected in request.form.getlist('MultiExistingItems'):
                query = "DELETE FROM [validation].[PalletItemList] WHERE ItemNumber = ?"
                parameters = selected
                bdp_sqlserver.sql_execute(query, parameters)
                flash('Item successfully deleted: ' + selected, "success")

    Availables = bhprd_sqlserver.get_rows("SELECT ITEMNMBR AS ItemNumber FROM IV00101")
    PalletItems = bdp_sqlserver.get_rows("SELECT [ItemNumber] FROM [validation].[PalletItemList]")
    Differences = [{'ItemNumber': x} for x in [x[0] for x in Availables] if x not in [x[0] for x in PalletItems]]
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('validation.palletitem.html', PalletItems=PalletItems, Differences=Differences, username=username))


@app.route('/validation/stirreritem', methods=['GET', 'POST'])
def validationStirrerItem():
    if request.method == 'POST':
        if request.form['submit_button'] == "Add":
            StirrerItem = request.form['AddItem']
            query = "INSERT INTO [validation].[StirrerItemList] (ItemNumber) VALUES (?)"
            parameters = StirrerItem
            bdp_sqlserver.sql_execute(query, parameters)
            flash('Item successfully added: ' + StirrerItem, "success")

        if request.form['submit_button'] == "Remove":
            for selected in request.form.getlist('MultiExistingItems'):
                query = "DELETE FROM [validation].[StirrerItemList] WHERE ItemNumber = ?"
                parameters = selected
                bdp_sqlserver.sql_execute(query, parameters)
                flash('Item successfully deleted: ' + selected, "success")

    Availables = bhprd_sqlserver.get_rows("SELECT ITEMNMBR AS ItemNumber FROM IV00101")
    StirrerItems = bdp_sqlserver.get_rows("SELECT [ItemNumber] FROM [validation].[StirrerItemList]")
    Differences = [{'ItemNumber': x} for x in [x[0] for x in Availables] if x not in [x[0] for x in StirrerItems]]
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('validation.stirreritem.html', StirrerItems=StirrerItems, Differences=Differences, username=username))


@app.route('/validation/palletcount', methods=['GET', 'POST'])
def validationPalletCount():
    if request.method == 'POST':
        ItemNumbers = [x for x in request.form if x[0:4] == "021-"]
        RequiredCounts = [request.form[x] for x in ItemNumbers]

        df = pd.DataFrame(
            {'ItemNumber': ItemNumbers,
             'RequiredCount': RequiredCounts}
        )

        df.to_sql(name='PalletCountStaging',
                  con=bdp_sqlserver.alchemy_engine(),
                  schema="validation",
                  if_exists="append",
                  method="multi",
                  index=False)

        query = "EXEC [validation].[UpdatePalletCount]"
        bdp_sqlserver.sql_execute(query)
        flash('Pallet Required Counts Updated', "success")

    PalletCounts = bdp_sqlserver.get_rows("SELECT ItemNumber,RequiredCount FROM data.ViewValidationPalletCounts")
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('validation.palletcount.html', PalletCounts=PalletCounts, username=username))