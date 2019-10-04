from bottle import Bottle, template, run, route, request, static_file
#from beaker import session
import sqlite3
from functools import wraps
from datetime import date
from marks import Marks
from beaker.middleware import SessionMiddleware

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
#app = Bottle()
app = SessionMiddleware(Bottle(), session_opts)
#app = SessionMiddleware(bottle.app(), session_opts)

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
gConn = sqlite3.connect('/home/angus/dcoda_net/cgi-bin/webMarks/cgi-bin/dcoda_acme.webMarks')
########################################################################

# static files ############################################
@route('/public/css/<filename>')
def server_static(filename):
	return static_file(filename, root="./public/css")

@route('/public/images/<filename>')
def server_static(filename):
	return static_file(filename, root="./public/images")
###########################################################

@route("/")
def index():
	pass

@route("/webMarks")
def indexWB():
	pass

@route("/searchMark")
def searchWebMark():
	pass

@route("/insertMark")
def addWebMark():
	pass

@route("/deltapass")
def deltaPass():
	pass

@route("/registration")
def registration():
	#return template('class_registration.html', errText="")
	return Marks().renderRegistrationView()

@route("/authorCred")
def authorCredFunc():
	(user_id,user_name) = pre_auth()
    #!!!additional logic for already present session needed
    ######################################################
	if user_id:
		authorize(user_id,user_name)
	else:
		return template('class_defaultpage',colorStyle="black", userName="", displayText="")

	return Marks().renderMainView()



def authorize():
	pass

### decorator functions
def authenticate(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		auth = request.authorization
		if not auth.username or not auth.password or not valid_credentials(auth.username, auth.password):
			return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
		return f(*args, **kwargs)
	return wrapper



def authorize(user_id,user_name):
#    sessionID = genSessionID();
	init_count = 0
	init_date_count = 0
	init_tab_state = 0
	session = bottle.request.environ.get('beaker.session')
	session['wmSessionID'] = sessionID
	session['wmUserID'] = user_id
	session['wmUserName'] = user_name
	session['Counter'] = init_count
	session['tab_state'] = init_tab_state
	session['dt_cnter'] = init_date_count
	session['expires'] = 0 
	session['domain'] =""
	sessionInstance = 'sess1'

def pre_auth():
	usr_name = request.params('user_name')
	usr_pass = request.params('user_pass')
	old_usr_pass = request.params('old_user_pass')
	exec_sql_str = str()

	if old_usr_pas:
		exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" + old_usr_pass +  "' and user_name ='"  + usr_name + "' "
	else:
		exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" + usr_pass + "' and user_name ='" + usr_name  + "' "

	### error checking ????? ##############
	curs = gConn.connect()
	curs.execute(exec_sql_str)
	user_row = curs.fetchall
#    row_count = curs.rows 


	return (user_row[0],user_row[1],usr_pass);

if __name__ ==  '__main__':
	#    app.run(debug="True", host="0.0.0.0", port='8081')
		run(debug=True, host="0.0.0.0", port='8085', reloader=True, server='gunicorn')
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


