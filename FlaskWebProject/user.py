class user:
    def __init__(self,bdp_sqlserver):
        self.Sessions = {}
        self.bdp_sqlserver = bdp_sqlserver

    def guest(self,SessionID):
        permissions = self.setPermissions(1)
        self.Sessions[SessionID] = {"username": "guest",
                  "userid": "1",
                  "permissions": permissions
        }


    def login(self,userid,username,SessionID):
        if username == "admin":
            self.Sessions[SessionID] = {
                "username": username,
                "userid": userid,
                "permissions": "full"
            }
        else :
            permissions = self.setPermissions(userid)
            self.Sessions[SessionID] ={
                    "username": username,
                    "userid": userid,
                    "permissions": permissions
                    }


    def setPermissions(self,userid):
        query = "EXEC [users].[PermissionsForUser] ?"
        parameters = userid
        permissions = [x[1] for x in self.bdp_sqlserver.get_rows(query, parameters) if x[2] == 1]
        return permissions




