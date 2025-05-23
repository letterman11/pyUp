import sqlite3
import mysql.connector
import pyodbc
import re
import time

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
dbConf = "stockDbConfig.dat" #@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
config_hash = {} #@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class db_factory(object):
    
    place = None 
    driver = None
    azure_db_wait = 70
    
    def __init__(self, config_file=None):
        self.config_file = config_file
        self.parse_config()

    def parse_config(self):

        if not self.config_file:
            self.config_file = dbConf

        try:
            config_file = open(self.config_file, 'r')

        except Exception:
            pass

        for line in config_file:

            if  re.match(r'^#',line):
                continue

            res = re.match(r'([A-Za-z_0-9]+)=([A-Za-z_0-9\*\-\/\.\*\:\\]+)',line)

            if res: 
                (key,value) = (res.group(1), res.group(2))

                config_hash[key] = value  
        config_file.close()
        
        db_factory.driver = self.db_driver()

        if re.match(r'sqlite3', self.db_driver()):
            db_factory.place = "?"

        elif re.match(r'mysql', self.db_driver()):
            db_factory.place = "%s"
        
        elif re.match(r'pyodbc', self.db_driver()):
            db_factory.place = "?"
            
        return config_hash

    def db_user(self):
        return config_hash['user']

    def db_passwd(self):
        return config_hash['password']

    def db_host(self):
        return config_hash['hostname']

    def db_name(self):
        return config_hash['database']

    def db_driver(self):
        return config_hash['driver']

    def db_port(self):
        return config_hash['port']

    def connect(self):

        if re.match(r'sqlite3', self.db_driver()):

            return sqlite3.connect(self.db_name())
          

        elif re.match(r'mysql', self.db_driver()):

            return  mysql.connector.connect(user=self.db_user(), password=self.db_passwd(),
                              host=self.db_host(),
                              database=self.db_name(),
                              port=self.db_port() or 3306 ,
                              #use_pure=False)
                              use_pure=True)

        elif re.match(r'pyodbc', self.db_driver()):

            conn=None
            user=self.db_user()
            password=self.db_passwd()
            host=self.db_host()
            database=self.db_name()

            #Using free tier Azure SQL which pauses db so retry needed to wakeup paused db
            # rough logic just to get past auto-pause of free tier
            connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};Encrypt=yes;TrustServerCertificate=no;ConnectionTimeout=120;ConnectionRetryCount=2'
            try:
                print("First Connection Call")
                conn =  pyodbc.connect(connectionString)
            except Exception as ex:
                print("Second Connection Call")
                time.sleep(db_factory.azure_db_wait)
                conn =  pyodbc.connect(connectionString)
            finally:
                if not conn:
                    Marks().renderDefaultView(red, "Database TimeOut")                    
                else:
                    print(conn)
                    return conn
