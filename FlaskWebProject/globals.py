from FlaskWebProject.data import data
from FlaskWebProject.user import user
from FlaskWebProject.settings import cfg

bdp_sqlserver = data(cfg['bdp_sqlserver'])
bhprd_sqlserver = data(cfg['bhprd_sqlserver'])
currentuser = user(bdp_sqlserver)

ShiftList = [
    {"Shift": "A", "Selected": 1},
    {"Shift": "B", "Selected": 0},
    {"Shift": "C", "Selected": 0},
    {"Shift": "D", "Selected": 0}
    ]




