from db import export_logs_csv
import pandas as pd
#import sklearn 
#import tensorflow as tf

DUMP_FILE_PATH = "S:\\SOAR\\Uploads\\exported.csv"

def load_csv(config): 
    """
    config = {}
    config['MYSQL_HOST'] = '127.0.0.1'
    config['MYSQL_USER'] = 'root'
    config['MYSQL_PASSWORD'] = 'root'
    config['MYSQL_DB'] = 'USERS'
    config['MYSQL_CURSORCLASS'] = 'DictCursor'
    csv_path = export_logs_csv(config)
    """
    csv_path = DUMP_FILE_PATH
    if csv_path != "":
        df = pd.read_csv(csv_path)
        print(df)
        return df
    
    else:
        return None



def evaluate_threat(arg = True):
    if(arg):
        return 1   
    return 0



