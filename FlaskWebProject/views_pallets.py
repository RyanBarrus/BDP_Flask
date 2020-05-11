from FlaskWebProject.globals import *
from flask import render_template, request, flash
from FlaskWebProject import app
import pandas as pd
from datetime import datetime


@app.route('/pallets/upload', methods=['GET', 'POST'])
def palletsUpload():
    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    if request.method == 'POST':
        ItemNumber = str(request.form['ItemNumber'])
        Pallet = str(request.form['PalletNumber'])
        Timestamp = str(datetime.now())
        CaseBarcodes = [x for x in request.form.getlist('cases') if x != '']
        CaseCount = len(CaseBarcodes)
        ChosenShift = request.form["Shift"]

        for shift in ShiftList :
            if ChosenShift == shift["Shift"]:
                shift["Selected"] = 1
            else:
                shift["Selected"] = 0

        df = pd.DataFrame(
            {'ItemNumber': [ItemNumber] * CaseCount,
             'CaseBarcode': CaseBarcodes,
             'Pallet': [Pallet] * CaseCount,
             'Shift': [ChosenShift] * CaseCount,
             'Timestamp': [Timestamp] * CaseCount,
             'UploadUsername': [username] * CaseCount
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
    return (render_template('pallets.upload.html', ItemList=ItemList, cases=cases, ShiftList=ShiftList, username=username))


@app.route('/pallets/range', methods=['GET', 'POST'])
def palletsRange():
    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    if request.method == 'POST':
        ItemNumber = request.form['ItemNumber']
        Pallet = request.form['PalletNumber']
        Timestamp = str(datetime.now())
        UploadUsername = username
        StartCase = request.form['StartCase']
        EndCase = request.form['EndCase']
        ChosenShift = request.form["Shift"]
        query = "EXEC [data].[RangeInsert] @ItemNumber =?, @Pallet=?, @Timestamp=?, @UploadUsername=?, @StartCase =?, @EndCase =?, @Shift = ?"
        parameters = (ItemNumber, Pallet, Timestamp, UploadUsername, StartCase, EndCase, ChosenShift)
        bdp_sqlserver.sql_execute(query,parameters)
        flash('Upload successful', "success")

        for shift in ShiftList:
            if ChosenShift == shift["Shift"]:
                shift["Selected"] = 1
            else:
                shift["Selected"] = 0

    ItemList = bdp_sqlserver.get_rows("SELECT [ItemNumber] FROM [validation].[RangeItemList]")
    return (render_template('pallets.range.html', ItemList=ItemList, ShiftList=ShiftList, username=username))

@app.route('/pallets/auto', methods=['GET', 'POST'])
def palletsAuto():
    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    if request.method == 'POST':
        ItemNumber = request.form['ItemNumber']
        Pallet = request.form['PalletNumber']
        Timestamp = str(datetime.now())
        UploadUsername = username
        InsertQuantity = request.form['InsertQuantity']
        ChosenShift = request.form["Shift"]
        query = "EXEC [data].[AutoInsert] @ItemNumber =?, @Pallet=?, @Timestamp=?, @UploadUsername=?, @InsertQuantity = ?, @Shift = ?"
        parameters = (ItemNumber, Pallet, Timestamp, UploadUsername, InsertQuantity, ChosenShift)
        bdp_sqlserver.sql_execute(query, parameters)
        flash('Upload successful', "success")

        for shift in ShiftList:
            if ChosenShift == shift["Shift"]:
                shift["Selected"] = 1
            else:
                shift["Selected"] = 0

    ItemList = bdp_sqlserver.get_rows("SELECT [ItemNumber] FROM [validation].[AutoItemList]")
    return (render_template('pallets.auto.html', ItemList=ItemList, ShiftList=ShiftList, username=username))


@app.route('/pallets/delete', methods=['GET', 'POST'])
def palletsDelete():
    palletDatas = None
    Selected = ""
    if request.method == 'POST':
        if request.form['submit_button'] == "View":
            query = "SELECT * FROM [data].[pallets] WHERE Pallet = ?"
            Selected = request.form['Pallet']
            parameters = Selected
            palletDatas = bdp_sqlserver.get_rows(query, parameters)
        if request.form['submit_button'] == "Delete":
            pallet = request.form['Pallet']
            palletDatas = None
            query = "DELETE FROM [data].[pallets] WHERE PALLET = ?"
            parameters = pallet
            bdp_sqlserver.sql_execute(query, parameters)
            flash('Successfully deleted pallet: ' + pallet, 'success')

    pallets = bdp_sqlserver.get_rows("SELECT Pallet, ROW_NUMBER() OVER (ORDER BY Timestamp DESC) AS Row FROM [data].[ViewPallets] ORDER BY Timestamp desc")
    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    return (render_template('pallets.delete.html', pallets=pallets, palletDatas=palletDatas, Selected=Selected, username=username))