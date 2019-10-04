import random
import pickle

def genSessionID():
	id_list = ('A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 
				'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9') 
	session_id  = str()
	rand_list = random.sample(id_list, 17)
	for i in rand_list:
		session_id = session_id + i
	return session_id

def storeSQL(sSQL):
    storedSQL =  sSQL
    sessionObject = validateSession()
    sessionObject['SESSIONDATA'] = storedSQL
    storeSessionObject(sessionObject) 

def getStoredSQL():

    sessionObject = validateSession()
    storedSQL = sessionObject['SESSIONDATA']
    return storedSQL or "['Fake Object']" 
def storeSessionObject(sessObj):
    return sessObj 


def validateSession():
	return {}
