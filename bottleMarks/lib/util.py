from sessionObject import *
import random
import pickle
import os

HOME = os.environ['HOME']

session_dir = HOME + '/pyprojects/webMarksMicro/bottleMarks/sessions'

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
    sessObject = validateSession()
    sessObject.SESSIONDATA = sSQL
    sessObject.SESSIONID = sessionID
    sessObject.USERID = USERID
    storeSessionObject(sessObject) 
'''
'''
def getStoredSQL(req):
    sessObj = validateSession()
    sessionID = req.get_cookie('wmSessionID')
    sessFile = open(session_dir + '/' +  str(sessionID), 'rb')
    sessObj = pickle.load(sessFile)
    storedSQL = sessObj.SESSIONDATA
    return storedSQL 

def storeSessionObject(sessObj):
    sessFile = open(session_dir +  '/' + str(sessObj.SESSIONID), 'wb')
    pickle.dump(sessObj,sessFile)
    return sessObj 


def validateSession():
    return SessionObject()

def validateSession2(req):
    #more error checks
    sessionID = req.get_cookie('wmSessionID')
    
    try:
        sessFile = open(session_dir + '/' + str(sessionID), 'rb')  
    except:

        return False 
    return True

def saveSession(sessionID):
    sessObj = SessionObject(sessionID)
    sessFile = open(session_dir + '/' + str(sessionID), 'wb')
    pickle.dump(sessObj,sessFile)
