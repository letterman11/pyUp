import random
import pickle
import os
import sys
from  lib.sessionObject import *

extra_path = '/pyprojects/webMarksMicro/py3x/bottleMarks/sessions'
extra_path_linux = '/pyprojects/webMarksMicro/py3x/bottleMarks/sessions'
extra_path_win32 = '\\webMarksMicro\\py3x\\bottleMarks\\sessions'

if sys.platform == 'win32':

    dir_sep = '\\'

    HOME = os.environ['HOMEPATH']  
    extra_path = extra_path_win32

elif sys.platform == 'linux':

    HOME = os.environ['HOME']  
    extra_path = extra_path_linux
    dir_sep = '/'

else:

    HOME = os.environ['HOME']  
    dir_sep = '/'

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
