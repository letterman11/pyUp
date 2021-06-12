import sqlite3
import mysql.connector
import re


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
dbConf = "stockDbConfig.dat" #@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
config_hash = {}

class db_factory(object):
    
    place = None 

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

            res = re.match(r'([A-Za-z_0-9]+)=([A-Za-z_0-9\-\/\.\:\\]+)',line)

            if res: 
                (key,value) = (res.group(1), res.group(2))
                #print(value)
                config_hash[key] = value  
        config_file.close()
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

    def connect(self):
#        self.parse_config()

        if re.match(r'sqlite3', self.db_driver()):
            db_factory.place = "?"
            return sqlite3.connect(self.db_name())
          

        elif re.match(r'mysql', self.db_driver()):
            db_factory.place = "%s"
            return  mysql.connector.connect(user=self.db_user(), password=self.db_passwd(),
                              host=self.db_host(),
                              database=self.db_name(),
                              use_pure=False)



