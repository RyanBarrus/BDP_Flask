from FlaskWebProject.globals import *
from flask import render_template, request, flash, url_for, redirect, make_response
from FlaskWebProject import app
from FlaskWebProject.settings import cfg
from hashlib import md5
import pandas as pd
import uuid



@app.before_request
def before_request():
    SessionID = request.cookies.get("SessionID")

    if SessionID not in currentuser.Sessions:
        SessionID = str(uuid.uuid4())
        currentuser.guest(SessionID)
        username = currentuser.Sessions[SessionID]['username']
        resp = make_response(render_template('user.login.html', username=username))
        resp.set_cookie('SessionID', SessionID)
        return resp
    else:
        currentuser.checkIn(SessionID)

    username = currentuser.Sessions[SessionID]['username']
    permissions = currentuser.Sessions[SessionID]['permissions']

    if username != 'admin' \
            and request.path[0:7] != "/static" \
            and request.path[0:6] != "/fetch" \
            and request.path[0:8] != "/favicon" \
            and request.path != "/" \
            and request.path != "/user/login" \
            and request.path != "/user/logout" \
            and request.path not in permissions:
        flash(username + " doesn't have permission to access " + request.path, "error")
        return redirect(url_for('userLogin'))

@app.route('/')
@app.route('/user/login', methods=['GET', 'POST'])
def userLogin():
    SessionID = request.cookies.get("SessionID")
    if request.method == 'POST':
        username = str(request.form['User Name'])
        hashedPassword = md5(request.form['Password'].encode('utf-8', 'ignore')).hexdigest()
        if username == "admin":
            if hashedPassword == cfg["AdminHashedPassword"]:
                userID = 0
                currentuser.login(userID, username, SessionID)
                flash('Successfully logged in as: ' + username, 'success')
            else :
                flash('Username or password incorrect', 'error')
        else :
            query = 'SELECT UserID FROM users.login WHERE UserName = ? AND HashedPassword = ?'
            parameters = (username, hashedPassword)
            loginResult = bdp_sqlserver.get_rows(query, parameters)
            if len(loginResult) == 0:
                flash('Username or password incorrect', 'error')
            else:
                userID = loginResult[0][0]
                currentuser.login(userID, username,SessionID)
                flash('Successfully logged in as: ' + username, 'success')

    username = currentuser.Sessions[SessionID]['username']
    return render_template('user.login.html', username=username)

@app.route('/user/create', methods=['GET', 'POST'])
def userCreate():
    if request.method == 'POST':
        username = str(request.form['User Name'])
        if username == 'admin':
            flash('Protected username: ' + username, 'error')
        else :
            hashedPassword = md5(request.form['Password'].encode('utf-8', 'ignore')).hexdigest()
            query = 'EXEC [users].[CreateUserIfNotExists] ?, ?'
            parameters = (username, hashedPassword)
            result = bdp_sqlserver.get_rows(query, parameters)[0][0]
            if result == 1:
                flash('Successfully created user: ' + username, 'success')
            else:
                flash('User already exists: ' + username, 'error')

    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
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

    users = bdp_sqlserver.get_rows("SELECT [UserID], [UserName] FROM [Users].[Login] WHERE UserName <> 'guest'")
    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    return (render_template('user.delete.html', users=users, username=username))

@app.route('/user/permissions', methods=['GET', 'POST'])
def userPermissions():
    permissionDatas = None
    userid = 1
    if request.method == 'POST':
        if request.form['submit_button'] == "View":
            query = "EXEC [users].PermissionsForUser @UserID = ?"
            userid = request.form['Users']
            parameters = userid
            permissionDatas = bdp_sqlserver.get_rows(query, parameters)

        if request.form['submit_button'] == "Update":
            selections = request.form.getlist('MultiUserPermisions')
            userid = request.form['Users']

            df = pd.DataFrame(
                {'UserID': [userid] * len(selections),
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
            currentuser.setPermissions(userid)

            query = "EXEC [users].PermissionsForUser @UserID = ?"
            parameters = userid
            permissionDatas = bdp_sqlserver.get_rows(query, parameters)
            flash('User permissions updated', "success")

        if request.form['submit_button'] == "SetDefaults":
            selections = request.form.getlist('MultiDefaultPermissions')
            userid = 1

            df = pd.DataFrame(
                {'UserID': [userid] * len(selections),
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
            currentuser.setPermissions(userid)
            flash('Default permissions updated', "success")

    users = bdp_sqlserver.get_rows("SELECT [UserID], [UserName] FROM [users].[login]")
    defaultPermissions = bdp_sqlserver.get_rows("EXEC [Users].DefaultPermissions")
    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    return render_template('user.permissions.html', users=users, permissionDatas=permissionDatas,
                           defaultPermissions=defaultPermissions, userid=userid, username=username)



@app.route('/user/logout')
def userLogout():
    SessionID = request.cookies.get("SessionID")
    currentuser.guest(SessionID)
    username = currentuser.Sessions[SessionID]['username']
    flash("Successfully logged out", "success")
    return render_template('user.login.html', username=username)



@app.route('/user/autologoutduration', methods=['GET', 'POST'])
def autoLogoutDuration():
    DurationMinutes = currentuser.autologout
    if request.method == 'POST':
        DurationMinutes = request.form['DurationMinutes']
        currentuser.setAutoLogout(int(DurationMinutes))
        flash('Success, new auto logout duration: ' + DurationMinutes + " minutes", "success")

    SessionID = request.cookies.get("SessionID")
    username = currentuser.Sessions[SessionID]['username']
    return render_template('user.autologoutduration.html', DurationMinutes=DurationMinutes, username=username)