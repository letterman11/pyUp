import datetime
import random
import pickle
import os
import sys
import re
import time
import hashlib
#from  lib.sessionObject import *
from  . sessionObject import *
from connection_factory import db_factory 

if sys.platform == 'win32':

    dir_sep = '\\'
    HOME = os.environ['HOMEPATH']  

elif sys.platform == 'linux':

    HOME = os.environ['HOME']  
    dir_sep = '/'

else:

    HOME = os.environ['HOME']  
    dir_sep = '\\'

place = db_factory().place

working_dir =  os.getcwd()
session_dir = working_dir + dir_sep +  "sessions"
print ("Session Dir " + session_dir)

sqlSelectSess = "select sessiondata,userid,rowcount,sort from session where sessionid = {} "
sqlSelectSessSQLServer = "select sessiondata,userid,row_count,sort from session where sessionid = {} "
sqlInsertSess = "insert into session ( sessionid,userid,DATE_TS )  values ( {}, {}, {} ) "
sqlUpdateSess = "update session set sessiondata = {},  UPDATE_TS =  {}  where sessionid = {} "

def digest_pass(passwd):
    if not passwd:
        passwd = ""
    sha_pad = hashlib.sha512()
    sha_pad.update(str.encode(passwd))
    return sha_pad.hexdigest()

def genSessionID():

    id_list = ('A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 
    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9') 
    session_id  = str()
    rand_list = random.sample(id_list, 17)

    for i in rand_list:
        session_id = session_id + i
    return session_id

def storeSQLDB(sSQL,req):

    sessionID = req.get_cookie('wmSessionID')
    USERID = req.get_cookie('wmUserID')
    sessObject = SessionObject()
    sessObject.SESSIONDATA = sSQL
    sessObject.SESSIONID = sessionID
    sessObject.USERID = USERID
    storeSessionObjectDB(sessObject) 

def getStoredSQLDB(req):

    sessObj = SessionObject()
    sessionID = req.get_cookie('wmSessionID')

    conn = db_factory().connect()
    curs = conn.cursor()

    try:
        curs.execute(sqlSelectSess.format(place), (sessionID,))
        res = curs.fetchone()
    except:
        conn.close()
        #return renderMainView(user_id,Error(103))
        return renderMainView("XXXXX",Error(103))

    finally:
        conn.close()

    storedSQL = res[0]

    return storedSQL 

def storeSessionObjectDB(sessObj):
    
    print("storeSessOBJ")
    conn = db_factory().connect()
    curs = conn.cursor()
    
    try:
        curs.execute(sqlUpdateSess.format(place,place,place), (sessObj.SESSIONDATA,datetime.datetime.now(),sessObj.SESSIONID))
    except:
        conn.rollback()
        return renderMainView(user_id,Error(103))
    else:
        conn.commit()
    finally:
        conn.close()

    return sessObj 

def validateSessionDB(req):
    sessionID = req.get_cookie('wmSessionID')

    conn = db_factory().connect()
    curs = conn.cursor()
    
    print("Validate val " + str(sessionID))

    res = None

    try:
        if db_factory.driver == 'pyodbc':
            curs.execute(sqlSelectSessSQLServer.format(place), (sessionID,))
        else:    
            curs.execute(sqlSelectSess.format(place), (sessionID,))
        res = curs.fetchone()
        print(sqlSelectSess.format(place))
    except Exception as ex:
        status = False
    else:
        if not res:
            status = False
        else:
            status = True
    finally:
        conn.close()

    return status

def saveSessionDB(sessionID,userID):

    conn = db_factory().connect()
    curs = conn.cursor()
    
    try:
        curs.execute(sqlInsertSess.format(place,place,place), (sessionID,userID,  datetime.datetime.now(),))
    except:
        conn.rollback()
        return renderMainView(userID,Error(102))
    else:
        conn.commit()
    finally:
        #pass
        conn.close()

def convertTime(dateAdded):
    (year, mon, day, hour, mins, secs)  = time.localtime( dateAdded/(1000 * 1000))[0:6]
    curr_date_tuple  = time.localtime( dateAdded/(1000 * 1000))
    day_of_week = time.strftime("%a",curr_date_tuple)
    dateAdded = ('{}-{}-{} {}:{}:{}').format(mon,day,year,hour,mins,secs)
    #dateAdded = ('{}-{}-{} {}:{}:{} {}').format(mon,day,year,hour,mins,secs, day_of_week)
    return dateAdded

def convertDateEpoch(humanDate):

    res1 = re.match(r'([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{4})',humanDate)

    res = re.match(r'([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})',humanDate)

    if res1:
        print(res1)
        month = res1.group(1) 
        day = res1.group(2) 
        year = res1.group(3)
    elif res:
        print(res)
        year = res.group(1) 
        month = res.group(2) 
        day = res.group(3)

    dateAdded = datetime.datetime(int(year),int(month),int(day),0,0).timestamp()
    dateAdded = int(dateAdded) * (1000 * 1000);

    return dateAdded


def isset(string):
    if (string != None) and len(string) == 0:
        return False 
    elif string == None:
        return False
    elif re.match(r"\s+$", string):
        return False
    else:
        return True 

def unWrap(req,reqObj):
    try:
        parmval = req.params[reqObj]
    except:
        return None
    return parmval 
