from FlaskWebProject.data import data
from FlaskWebProject.user import user
from FlaskWebProject.settings import cfg

bdp_sqlserver = data(cfg['bdp_sqlserver'])
bhprd_sqlserver = data(cfg['bhprd_sqlserver'])
currentuser = user(bdp_sqlserver)



