from bottle import Bottle, template, run, route, request, response, static_file
from datetime import datetime
from marks import Marks
from functools import wraps
from  PJJExecPageSQL import *
import lib.util as util 
import time
import sqlite3
from  globals import *
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

########################################################################
# global database name 
#connFile = gConn =  webmarksDB = sqlite3.connect('/home/angus/dcoda_net/cgi-bin/webMarks/cgi-bin/dcoda_acme.webMarks')
#connFile = gConn =  webmarksDB = '/home/angus/dcoda_net/cgi-bin/webMarks/cgi-bin/dcoda_acme.webMarks'
#connFile = gConn =  webmarksDB = '/home/angus/pyprojects/webMarksMicro/bottleMarks/dcoda_acme.webMarks'
########################################################################


### decorator functions
def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if validate_session() == False:
            return Marks().renderDefaultView()
        return f(*args, **kwargs)
    return wrapper


def pre_auth(connFile):
    usr_name = "" 
    usr_pass = ""
    old_usr_pass = ""
    usr_id = ""
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
	
    print usr_name  + "User Name"
    print usr_pass + "User PASS"

    if user_row:
        user_row= user_row[0]
        print user_row
        print "user row list above"
        usr_id,usr_name = user_row[0],user_row[1]
        return (usr_id,usr_name)
    else:
        return None

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
    return Marks().renderRegistrationView()


@app.route('/default')
def logIn():
    return Marks().renderDefaultView()
    #return renderDefaultView()

@app.route("/")
@authenticate
def index():
    return renderMainView()
#    return Marks().renderMainView()

@app.route("/webMarks")
@authenticate
def indexWB():
    return renderMainView()

@app.route("/tabView")
@authenticate
def index():
    return renderMainView()

@app.post("/searchMark")
@authenticate
def searchWebMark():
    return renderMainView()

@app.post("/insertMark")
@authenticate
#def addWebMark(request=None):
def addWebMark():
    user_id = request.get_cookie('wmUserID')	
    title = request.params['mark_title']	
    url = request.params['mark_url']	
    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    dateAdded = unix_epochs * (1000 * 1000)

    conn = sqlite3.connect(connFile)
    curs = conn.cursor()

    curs.execute("select max(BOOKMARK_ID) from WM_BOOKMARK")
    (tbl1MaxId,) = curs.fetchone()
    curs.execute("select max(PLACE_ID) from WM_PLACE")
    (tbl2MaxId,) = curs.fetchone()

    print tbl1MaxId
    print tbl2MaxId

    tbl1MaxId +=1
    tbl2MaxId +=1

    curs.execute("select b.url from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ? and b.URL =  ? ", (user_id, url))
    dup_check = curs.fetchone()
    
    if dup_check:
        print "Duplicate"
        return renderMainView(user_id,Error(150))
    
    try:
        curs.execute("insert into WM_PLACE (PLACE_ID, URL, TITLE) values (?,?,?)", (tbl2MaxId, url, title,))
    except:
        print "Insert Error wmplace"
        return renderMainView(user_id,Error(2000))

    try:
        curs.execute("insert into WM_BOOKMARK (BOOKMARK_ID, USER_ID, PLACE_ID, TITLE, DATEADDED) values (?,?,?,?,?)", (tbl1MaxId, user_id, tbl2MaxId, title, dateAdded,))
    except:
        print "Insert Error Error Error wmboookmark"
        return renderMainView(user_id,Error(2000))
    conn.commit()
    conn.close()
      
    return renderMainView()

@app.post("/deltapass")
@authenticate
def deltaPass():
    pass

@app.route("/logout")
def logOut():
    return Marks().renderDefaultView()

@app.post("/authenCred")
def authenCredFunc():
    result_row = pre_auth(gConn)
    user_id = None
    if result_row:
        (user_id,user_name) = result_row
    #!!!additional logic for already present session needed
    ######################################################
    if user_id:
        authorize(user_id,user_name)
    else:
        return Marks().renderDefaultView(colorStyle="red",displayText="Failed Login")
        #return template('class_defaultpage', colorStyle="red", userName="",displayText="Failed Login")
    return renderMainView(user_id)

def validate_session():
    wmSID = request.get_cookie('wmSessionID')
    user_id = request.get_cookie('wmUserID')
    #print  "SessionID" +  " " + wmSID
    if not wmSID:
        return False

def authorize(user_id,user_name):
    print user_id[1] 
    print "Loot"
    print user_id[0] 
    print "Looter"
    sessionID = util.genSessionID()
    init_count = 0
    init_date_count = 0
    init_tab_state = 0
    response.set_cookie('wmSessionID',str(sessionID))
    response.set_cookie('wmUserID',str(user_id))
    response.set_cookie('wmUserName', str(user_name))
    response.set_cookie('Counter', str(init_count))
    response.set_cookie('tab_state', str(init_tab_state))
    response.set_cookie('dt_cnter', str(init_date_count))
#    reponse.set_cookie('expires', None)
#    reponse.set_cookie('domain', None)

def renderMainView(user_id=None,errObj=None):
    user_id=None
    user_name=None
    try:
        user_name = request.params['user_name']
    except:
        pass
    if not user_id or not user_name:
        user_id = request.get_cookie('wmUserID')
        user_name = request.get_cookie('wmUserName')
    return exec_page(request,user_id,user_name,errObj)

if __name__ ==  '__main__':
#        app.run(debug="True", host="0.0.0.0", port='8086')
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


