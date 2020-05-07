class user:
    def __init__(self,bdp_sqlserver):
        self.ip_users = {}
        self.bdp_sqlserver = bdp_sqlserver

    def guest(self,ip):
        permissions = self.setPermissions(1)
        self.ip_users[ip] = {"username": "guest",
                  "userid": "1",
                  "permissions": permissions
        }


    def login(self,userid,username,ip):
        permissions = self.setPermissions(userid)
        self.ip_users[ip] ={
                "username": username,
                "userid": userid,
                "permissions": permissions
                }


    def setPermissions(self,userid):
        query = "EXEC [users].[PermissionsForUser] ?"
        parameters = userid
        permissions = [x[1] for x in self.bdp_sqlserver.get_rows(query, parameters) if x[2] == 1]
        return permissions




