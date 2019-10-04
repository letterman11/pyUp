import random


def genSessionID():
	id_list = ('A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 
				'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9') 
	session_id  = str()
#	print id_list
	rand_list = random.sample(id_list, 17)
	for i in rand_list:
		session_id = session_id + i
#	print rand_list
#	print session_id

def storeSession():
	pass


def validateSession():
	pass

#genSessionID()
