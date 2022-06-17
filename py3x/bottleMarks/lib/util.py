import datetime
import random
import pickle
import os
import sys
import re
import time
from  lib.sessionObject import *

if sys.platform == 'win32':

    dir_sep = '\\'
    HOME = os.environ['HOMEPATH']  

elif sys.platform == 'linux':

    HOME = os.environ['HOME']  
    dir_sep = '/'

else:

    HOME = os.environ['HOME']  
    dir_sep = '\\'

working_dir =  os.getcwd()
session_dir = working_dir + dir_sep +  "sessions"
print ("Session Dir " + session_dir)

def genSessionID():

    id_list = ('A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 
    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9') 
    session_id  = str()
    rand_list = random.sample(id_list, 17)

    for i in rand_list:
        session_id = session_id + i
    return session_id

def storeSQL(sSQL,req):

    sessionID = req.get_cookie('wmSessionID')
    USERID = req.get_cookie('wmUserID')
    sessObject = SessionObject()
    sessObject.SESSIONDATA = sSQL
    sessObject.SESSIONID = sessionID
    sessObject.USERID = USERID
    storeSessionObject(sessObject) 

def getStoredSQL(req):

    sessObj = SessionObject()
    sessionID = req.get_cookie('wmSessionID')
    sessFile = open(session_dir + dir_sep +  str(sessionID), 'rb')
    sessObj = pickle.load(sessFile)
    storedSQL = sessObj.SESSIONDATA
    return storedSQL 

def storeSessionObject(sessObj):
    sessFile = open(session_dir +  dir_sep + str(sessObj.SESSIONID), 'wb')
    pickle.dump(sessObj,sessFile)
    sessFile.close()
    return sessObj 

def getSessionObject(sessionID):
    sessFile = open(session_dir +  dir_sep + str(sessObj.SESSIONID), 'wb')
    sessObj = pickle.load(sessFile)
    sessFile.close()
    return sessObj 


def validateSession2(req):
    sessionID = req.get_cookie('wmSessionID')

    try:
        sessFile = open(session_dir + dir_sep + str(sessionID), 'rb')  
    except:
        status = False
    else:
        status = True
        sessFile.close()

    return status

def saveSession(sessionID):
    sessObj = SessionObject(sessionID)
    sessFile = open(session_dir + dir_sep + str(sessionID), 'wb')
    pickle.dump(sessObj,sessFile)
    sessFile.close()

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
