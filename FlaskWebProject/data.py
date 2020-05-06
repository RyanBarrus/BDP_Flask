import pyodbc
from sqlalchemy import create_engine
from urllib.parse import quote_plus

class data:

    def __init__(self,cfg_server):
        self.sqlServerName = cfg_server['SqlServerName']
        self.database = cfg_server['Database']
        self.uid = cfg_server['db_uid']
        self.pwd = cfg_server['db_pwd']

    def connect(self):
        drivers = [item for item in pyodbc.drivers()]
        driver = drivers[-1]
        conn = pyodbc.connect(f'Driver={driver};Server={self.sqlServerName};Database={self.database};uid={self.uid};pwd={self.pwd};')
        return conn

    def get_rows(self,query,parameters = None) :
        conn = self.connect()
        results = []
        cursor = conn.cursor()
        if not parameters:
            cursor.execute(query)
        else :
            cursor.execute(query,parameters)
        for row in cursor:
            results.append(row)
        conn.commit()
        cursor.close()
        conn.close()
        return results

    def sql_execute(self, query, parameters=None) :
        conn = self.connect()
        cursor = conn.cursor()
        if not parameters:
            cursor.execute(query)
        else:
            cursor.execute(query,parameters)
        conn.commit()
        cursor.close()
        conn.close()

    def alchemy_engine(self):
        quoted = quote_plus(f"Driver={{SQL Server}};Server={self.sqlServerName};Database={self.database};uid={self.uid};pwd={self.pwd};")
        engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        return engine
