class user:
    def __init__(self,bdp_sqlserver):
        self.username = "guest"
        self.userid = 1
        self.bdp_sqlserver = bdp_sqlserver
        self.setPermissions()

    def login(self,userid,username):
        self.userid = userid
        self.username = username
        self.setPermissions()

    def setPermissions(self):
        query = "EXEC [users].[PermissionsForUser] ?"
        parameters = self.userid
        self.permissions = [x[1] for x in self.bdp_sqlserver.get_rows(query, parameters) if x[2] == 1]





