from FlaskWebProject.globals import *
from flask import render_template, request, flash, url_for, redirect, session
from FlaskWebProject import app
from hashlib import md5
import pandas as pd


@app.before_request
def before_request():
    ip = request.remote_addr
    if ip not in currentuser.ip_users:
        currentuser.guest(ip)
    username = currentuser.ip_users[ip]['username']
    permissions = currentuser.ip_users[ip]['permissions']

    if username != 'admin' \
            and request.path[0:7] != "/static" \
            and request.path[0:6] != "/fetch" \
            and request.path[0:8] != "/favicon" \
            and request.path != "/" \
            and request.path != "/user/login" \
            and request.path not in permissions:
        flash(username + " doesn't have permission to access " + request.path, "error")
        return redirect(url_for('userLogin'))

@app.route('/user/login', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        username = str(request.form['User Name'])
        hashedPassword = md5(request.form['Password'].encode('utf-8', 'ignore')).hexdigest()
        query = 'SELECT UserID FROM users.login WHERE UserName = ? AND HashedPassword = ?'
        parameters = (username, hashedPassword)
        loginResult = bdp_sqlserver.get_rows(query, parameters)
        if len(loginResult) == 0:
            flash('Username or password incorrect', 'error')
        else:
            userID = loginResult[0][0]
            currentuser.login(userID, username,request.remote_addr)
            flash('Successfully logged in as: ' + username, 'success')
    username = currentuser.ip_users[request.remote_addr]['username']
    return render_template('user.login.html', username=username)

@app.route('/user/create', methods=['GET', 'POST'])
def userCreate():
    if request.method == 'POST':
        username = str(request.form['User Name'])
        hashedPassword = md5(request.form['Password'].encode('utf-8', 'ignore')).hexdigest()
        query = 'EXEC [users].[CreateUserIfNotExists] ?, ?'
        parameters = (username, hashedPassword)
        result = bdp_sqlserver.get_rows(query, parameters)[0][0]
        if result == 1:
            flash('Successfully created user: ' + username, 'success')
        else:
            flash('User already exists: ' + username, 'error')
    username = currentuser.ip_users[request.remote_addr]['username']
    return render_template('user.create.html', username=username)

@app.route('/user/delete', methods=['GET', 'POST'])
def userDelete():
    if request.method == 'POST':
        for selected in request.form.getlist('MultiSelect'):
            print(selected)
            query = "DELETE FROM [users].[Login] WHERE UserID = ?"
            parameters = selected
            bdp_sqlserver.sql_execute(query, parameters)

        flash('Users successfully deleted', "success")

    users = bdp_sqlserver.get_rows("SELECT [UserID], [UserName] FROM [Users].[Login]")
    username = currentuser.ip_users[request.remote_addr]['username']
    return (render_template('user.delete.html', users=users, username=username))

@app.route('/user/permissions', methods=['GET', 'POST'])
def userPermissions():
    permissionDatas = None
    if request.method == 'POST':
        if request.form['submit_button'] == "View":
            query = "EXEC [users].PermissionsForUser @UserID = ?"
            parameters = request.form['Users']
            permissionDatas = bdp_sqlserver.get_rows(query, parameters)

        if request.form['submit_button'] == "Update":
            selections = request.form.getlist('MultiUserPermisions')
            UserID = request.form['Users']

            df = pd.DataFrame(
                {'UserID': [UserID] * len(selections),
                 'PermissionID': selections}
            )

            df.to_sql(name='PermissionsAssignmentStaging',
                      con=bdp_sqlserver.alchemy_engine(),
                      schema="users",
                      if_exists="append",
                      method="multi",
                      index=False)

            query = "EXEC [users].UpdatePermissionsForUser"
            bdp_sqlserver.sql_execute(query)
            currentuser.setPermissions(UserID)

            flash('Permissions updated', "success")

        if request.form['submit_button'] == "SetDefaults":
            selections = request.form.getlist('MultiDefaultPermissions')
            UserID = 1

            df = pd.DataFrame(
                {'UserID': [UserID] * len(selections),
                 'PermissionID': selections}
            )

            df.to_sql(name='PermissionsAssignmentStaging',
                      con=bdp_sqlserver.alchemy_engine(),
                      schema="users",
                      if_exists="append",
                      method="multi",
                      index=False)

            query = "EXEC [users].UpdateDefaultPermissions"
            bdp_sqlserver.sql_execute(query)
            currentuser.setPermissions(UserID)
            flash('Permissions updated', "success")

    users = bdp_sqlserver.get_rows("SELECT [UserID], [UserName] FROM [users].[login]")
    defaultPermissions = bdp_sqlserver.get_rows("EXEC [Users].DefaultPermissions")
    username = currentuser.ip_users[request.remote_addr]['username']
    return render_template('user.permissions.html', users=users, permissionDatas=permissionDatas,
                           defaultPermissions=defaultPermissions, username=username)
