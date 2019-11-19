from sessionObject import *
import random
import pickle
import globals

def genSessionID():
	id_list = ('A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 
				'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9') 
	session_id  = str()
	rand_list = random.sample(id_list, 17)
	for i in rand_list:
		session_id = session_id + i
	return session_id
'''
def storeSQL(sSQL):
    storedSQL =  sSQL
    sessObject = validateSession()
    sessObject.SESSIONDATA = storedSQL
    storeSessionObject(sessObject) 
'''
def storeSQL(sSQL,req):
    sessionID = req.get_cookie('wmSessionID')
    USERID = req.get_cookie('wmUserID')
    sessObject = validateSession()
    sessObject.SESSIONDATA = sSQL
    sessObject.SESSIONID = sessionID
    sessObject.USERID = USERID
    storeSessionObject(sessObject) 
'''
def getStoredSQL():
    sessObj = validateSession()
#    print "################## SID #########################  " + sessObj.SESSIONID
    sessFile = open(str(sessObj.SESSIONID), 'rb')
    sessObj = pickle.load(sessFile)
    storedSQL = sessObj.SESSIONDATA
#    print "################## StoreSQL #########################  " + storedSQL
#    print "################## SID #########################  " + sessObj.SESSIONID
    return storedSQL or "['Fake Object']" 
'''
def getStoredSQL(req):
    sessObj = validateSession()
    sessionID = req.get_cookie('wmSessionID')
    print "################## SID #########################  " + sessionID
    sessFile = open(str(sessionID), 'rb')
    sessObj = pickle.load(sessFile)
    storedSQL = sessObj.SESSIONDATA
    print "################## StoreSQL #########################  " + storedSQL
    print "################## SID #########################  " + sessObj.SESSIONID
    return storedSQL or "['Fake Object']" 

def storeSessionObject(sessObj):
    sessFile = open(str(sessObj.SESSIONID), 'wb')
    pickle.dump(sessObj,sessFile)
    return sessObj 


def validateSession():
    return SessionObject(sessionID=globals.sessionID)

