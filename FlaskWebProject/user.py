from datetime import datetime, timedelta
import threading, time

class user:
    def __init__(self,bdp_sqlserver):
        self.Sessions = {}
        self.autologout = 1
        self.bdp_sqlserver = bdp_sqlserver
        threading.Thread(target=self.logoutInactive).start()

    def guest(self,SessionID):
        permissions = self.setPermissions(1)
        self.Sessions[SessionID] = {"username": "guest",
                  "userid": "1",
                  "permissions": permissions,
                  "lastactivity": datetime.now()
        }

    def login(self,userid,username,SessionID):
        if username == "admin":
            self.Sessions[SessionID] = {
                "username": username,
                "userid": userid,
                "permissions": "full",
                "lastactivity": datetime.now()
            }
        else :
            permissions = self.setPermissions(userid)
            self.Sessions[SessionID] ={
                    "username": username,
                    "userid": userid,
                    "permissions": permissions,
                    "lastactivity": datetime.now()
                    }

    def setPermissions(self,userid):
        query = "EXEC [users].[PermissionsForUser] ?"
        parameters = userid
        permissions = [x[1] for x in self.bdp_sqlserver.get_rows(query, parameters) if x[2] == 1]
        return permissions

    def checkIn(self,SessionID):
        self.Sessions[SessionID]["lastactivity"] = datetime.now()

    def setAutoLogout(self,autologout):
        self.autologout = autologout

    def logoutInactive(self):
        while (True):
            time.sleep(300)
            for Session in self.Sessions:
                duration = datetime.now() - self.Sessions[Session]['lastactivity']
                if duration > timedelta(minutes=60) and self.Sessions[Session]['userid'] != 1:
                    self.guest(Session)










