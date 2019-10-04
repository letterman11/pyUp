from bottle import Bottle, template, run, route, request, response, static_file
import sqlite3
from datetime import date
from marks import Marks
from functools import wraps
#from authen import *
import util

app = Bottle()

########################  SQL STRINGS ####################################
main_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ? and  ("
hist_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  "; 
date_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  order by a.dateAdded desc limit 100"
date_sql_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ?  order by a.dateAdded "


AE_str = " a.title like 'A%' or  a.title like 'a%' or  a.title like 'B%' or  a.title like 'b%' or  a.title like 'C%' or  a.title like 'c%' or  a.title like 'D%' or  a.title like 'd%'  or  a.title like 'E%' or  a.title like 'e%'"
FJ_str = " a.title like 'F%' or  a.title like 'f%'  or  a.title like 'G%' or  a.title like 'g%'  or  a.title like 'H%' or  a.title like 'h%'  or  a.title like 'I%' or  a.title like 'i%'  or  a.title like 'J%' or  a.title like 'j%'"
KP_str = " a.title like 'K%' or  a.title like 'k%'  or  a.title like 'L%' or  a.title like 'l%'  or  a.title like 'M%' or  a.title like 'm%'  or  a.title like 'N%' or  a.title like 'n%'  or  a.title like 'O%' or  a.title like 'o%'or  a.title like 'P%' or  a.title like 'p%'"
QU_str = " a.title like 'Q%' or  a.title like 'q%'  or  a.title like 'R%' or  a.title like 'r%'  or  a.title like 'S%' or  a.title like 's%'  or  a.title like 'T%' or  a.title like 't%'  or  a.title like 'U%' or  a.title like 'u%'"
VZ_str = " a.title like 'V%' or  a.title like 'v%'  or  a.title like 'W%' or  a.title like 'w%'  or  a.title like 'X%' or  a.title like 'x%'  or  a.title like 'Y%' or  a.title like 'y%'  or  a.title like 'Z%' or  a.title like 'z%'"

ORDER_BY_TITLE =  " ) order by a.title "
ORDER_BY_DATE =  " ) order by a.dateAdded "
########################  SQL STRINGS ####################################

tabMap = {'tab_AE':1,'tab_FJ':2,'tab_KP':3,'tab_QU':4,'tab_VZ':5,'tab_SRCH_TITLE':6,'tab_SRCH_URL':7,'tab_SRCH_DATE':8,'tab_DATE':9,'searchBox':10}

########################################################################
# global database handle
global gConn
#gConn = sqlite3.connect('/home/angus/dcoda_net/cgi-bin/webMarks/cgi-bin/dcoda_acme.webMarks')
gConn = webMarksDB = '/home/angus/dcoda_net/cgi-bin/webMarks/cgi-bin/dcoda_acme.webMarks'
########################################################################


### decorator functions
def authenticate(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		#(user_id,user_name)= pre_auth(gConn)
		if not pre_auth(webMarksDB) or  not validate_session():
			return Marks().renderDefaultView()
		return f(*args, **kwargs)
	return wrapper


def pre_auth(connFile):
	usr_name = "" 
	usr_pass = ""
	old_usr_pass = ""
	try:
		usr_name = request.params['user_name'] 
		usr_pass = request.params['user_pass'] 
		old_usr_pass = request.params['old_user_pass']  
	except:
		pass		
	exec_sql_str = str()

	if old_usr_pass:
		exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" + old_usr_pass +  "' and user_name ='"  + usr_name + "' "
	else:
		exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" + usr_pass + "' and user_name ='" + usr_name  + "' "

	### error checking ????? ##############
	conn = sqlite3.connect(connFile)
	curs = conn.cursor()
	curs.execute(exec_sql_str)
	user_row = curs.fetchall()
	conn.close()

	print usr_name
	print usr_pass + "User PASS"
	return user_row


# static files ############################################
@app.route('/public/css/<filename>')
def server_static(filename):
	return static_file(filename, root="./public/css")

@app.route('/public/images/<filename>')
def server_static(filename):
	return static_file(filename, root="./public/images")

@app.route('/public/js/<filename>')
def server_static(filename):
	return static_file(filename, root="./public/js")
###########################################################

@app.route('/registration')
def register():
	return template('class_registration.html', errText="")
#	return Marks().renderRegistrationView()


@app.route('/default')
def logIn():
	return Marks().renderDefaultView()

@app.route("/")
@authenticate
def index():
	return Marks().renderMainView()

@app.route("/webMarks")
@authenticate
def indexWB():
	pass

@app.route("/searchMark")
@authenticate
def searchWebMark():
	pass

@app.route("/insertMark")
@authenticate
def addWebMark():
	pass

@app.route("/deltapass")
@authenticate
def deltaPass():
	pass

@app.route("/logout")
def logOut():
	pass

@app.post("/authenCred")
def authenCredFunc():
	(user_id) = pre_auth(gConn)
    #!!!additional logic for already present session needed
    ######################################################
	if user_id:
		authorize(user_id)
	else:
		return template('class_defaultpage', colorStyle="red", userName="",displayText="Failed Login")

	return Marks().renderMainView(user_id, 0,tabMap)



def validate_session():
	wmSID = request.cookie('wmSessionID')
	if not wmSID:
		return False

def authorize(user_id):
	sessionID = util.genSessionID()
	init_count = 0
	init_date_count = 0
	init_tab_state = 0
	response.set_cookie('wmSessionID',str(sessionID))
	response.set_cookie('wmUserID',str(user_id))
	response.set_cookie('wmUserName', str(user_id))
	response.set_cookie('Counter', str(init_count))
	response.set_cookie('tab_state', str(init_tab_state))
	response.set_cookie('dt_cnter', str(init_date_count))
#	reponse.set_cookie('expires', None)
#	reponse.set_cookie('domain', None)

if __name__ ==  '__main__':
#	    app.run(debug="True", host="0.0.0.0", port='8086')
		app.run(debug="True", host="0.0.0.0", port='8086', reloader=True, server='gunicorn')
'''
def authenticate(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		auth = request.authorization
		if not auth.username or not auth.password or not valid_credentials(auth.username, auth.password):
			return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
		return f(*args, **kwargs)
	return wrapper

'''


