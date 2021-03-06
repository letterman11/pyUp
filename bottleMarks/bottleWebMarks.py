from bottle import Bottle, template, run, route, request, response, static_file
from datetime import datetime
from marks import Marks
from functools import wraps
from  PJJExecPageSQL import exec_page
import lib.util as util 
import time
import sqlite3
from  globals import *
from error import *

app = Bottle()

# static files ############################################
@app.route('/public/css/<filename>')
def server_static_css(filename):
    return static_file(filename, root="./public/css")
     
@app.route('/public/images/<filename>')
def server_static_imgs(filename):
    return static_file(filename, root="./public/images")

@app.route('/public/js/<filename>')
def server_static_js(filename):
    return static_file(filename, root="./public/js")
###########################################################

### decorator functions
def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        #if validate_session() == False:
        if validate_session2(request) == False:
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

    if old_usr_pass: # for update
        exec_sql_str = "select user_id, user_name, user_passwd from WM_USER where user_passwd = '" + old_usr_pass +  "' and user_name ='"  + usr_name + "' "
    else:
        exec_sql_str = "select user_id, user_name, user_passwd from WM_USER where user_passwd = '" + usr_pass + "' and user_name ='" + usr_name  + "' "

    ### error checking ????? ##############
    conn = sqlite3.connect(connFile)
    curs = conn.cursor()
    curs.execute(exec_sql_str)
    user_row = curs.fetchall()
    conn.close()
	
    if user_row:
        user_row= user_row[0]
        print user_row
        print "user row list above"
        usr_id,usr_name,usr_pass = user_row[0],user_row[1],user_row[2]
        return (usr_id,usr_name,usr_pass)
    else:
        return None

@app.route('/registration')
def register():
    return Marks().renderRegistrationView()

@app.route('/regAuth')
def registerAuth():
	pass
#    return Marks().renderRegistrationView()

@app.route('/default')
def logIn():
    return Marks().renderDefaultView()
    #return renderDefaultView()

##################################################################
###  --  Authenticated routes -- via authenticate decorator -- ###
##################################################################

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
def indexView():
    return renderMainView()

@app.post("/searchMark")
@authenticate
def searchWebMark():
    return renderMainView()

@app.post("/insertMark")
@authenticate
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
    except Exception as ex:
        print "Insert Error wmplace"
        return renderMainView(user_id,Error(2000))

    try:
        curs.execute("insert into WM_BOOKMARK (BOOKMARK_ID, USER_ID, PLACE_ID, TITLE, DATEADDED) values (?,?,?,?,?)", (tbl1MaxId, user_id, tbl2MaxId, title, dateAdded,))
    except Exception:
        print "Insert Error Error Error wmboookmark"
        return renderMainView(user_id,Error(2000))
    else:
        conn.commit()
    finally:
        conn.close()
      
    return renderMainView()

@app.post("/updateMark")
@authenticate
def updateMark():
    user_id = request.get_cookie('wmUserID')
    title = request.params['title_update']
    url = request.params['url_update']
    tblBookMarkId = request.params['bk_id']
    print tblBookMarkId
 
    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    dateAdded = unix_epochs * (1000 * 1000)

    conn = sqlite3.connect(connFile)
    curs = conn.cursor()

    try:
        curs.execute("select PLACE_ID from WM_BOOKMARK where BOOKMARK_ID = ?", (tblBookMarkId,))

    except Exception as ex:
        print "error execute update"
        raise ex
        return renderMainView(user_id,Error(153))

    (tblPlaceId,) = curs.fetchone()
    print "PlaceID " + str(tblPlaceId)

    try:
        curs.execute("update WM_BOOKMARK set TITLE = ? where BOOKMARK_ID = ? ", (title, tblBookMarkId,))
        curs.execute("update WM_PLACE set  URL = ? , TITLE = ? where PLACE_ID = ? ", (url, title,tblPlaceId,))
    except Exception as ex:
        raise ex
        return renderMainView(user_id,Error(153))
    else:
        conn.commit()
    finally:
        conn.close()
 
    return renderMainView()


@app.post("/deleteMark")
@authenticate
def deleteMark():
    user_id = request.get_cookie('wmUserID')
    tblBookMarkId = request.params['bk_id']

    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    dateAdded = unix_epochs * (1000 * 1000)
    conn = sqlite3.connect(connFile)
    curs = conn.cursor()

    try:
        curs.execute("select PLACE_ID from WM_BOOKMARK where BOOKMARK_ID = ?", (tblBookMarkId,))

    except Exception as ex:
        print "error execute select in deleteMark"
        raise ex
        return renderMainView(user_id,Error(153))

    (tblPlaceId,) = curs.fetchone()
    print "PlaceID " + str(tblPlaceId)


    conn = sqlite3.connect(connFile)
    curs = conn.cursor()

    try:
        curs.execute("delete from  WM_PLACE  where PLACE_ID = ? ", (tblPlaceId,))
        curs.execute("delete from  WM_BOOKMARK  where BOOKMARK_ID = ? ", (tblBookMarkId,))

    except Exception as ex:
        print "error execute delettion"
        raise ex
        return renderMainView(user_id,Error(153))

    else:
        conn.commit()
    finally:
        conn.close()
 
    return renderMainView()


@app.post("/deltaPass")
@authenticate
def deltaPass():
    print connFile
    try:
        (user_id,user_name,user_pass) = pre_auth(connFile)
    except:
        return renderMainView(request.params['user_name'],Error(112))
   
    new_passwd = request.params['user_pass']

    if not user_id:
        return renderMainView(Error(user_id,112))
    else:
        try:
            conn = sqlite3.connect(connFile)
            curs = conn.cursor()
            curs.execute("update WM_USER set USER_PASSWD = ?  where USER_NAME = ? ", (new_passwd,user_name));

        except:
            return renderMainView(user_id,Error(2000))
        else:
            conn.commit()
        finally:
            conn.close()
    return renderMainView()

######################################################################
## end authenticated routes via decorator ############################
######################################################################

@app.route("/logout")
def logOut():
    return Marks().renderDefaultView()

@app.post("/authenCred")
def authenCredFunc():
    result_row = pre_auth(gConn)
    user_id = None
    if result_row:
        (user_id,user_name,user_pass) = result_row
    #!!!additional logic for already present session needed
    ######################################################
    if user_id:
        authorize(user_id,user_name)
    else:
        return Marks().renderDefaultView(colorStyle="red",displayText="Incorrect User ID/Password")
    return renderMainView(user_id)

def validate_session():
    wmSID = request.get_cookie('wmSessionID')
    user_id = request.get_cookie('wmUserID')
    if not wmSID:
        return False

def validate_session2(req):
    return util.validateSession2(req) 

def authorize(user_id,user_name):
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
    util.saveSession(sessionID)
#    response.set_cookie('expires', 60*60)
#    reponse.set_cookie('domain', None)

def renderMainView(user_id=None,errObj=None):
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
        app.run(debug=True, host="0.0.0.0", port='8086', reloader=True, server='gunicorn', workers=3)
#        app.run(debug="True", host="0.0.0.0", port='8086', reloader=True, server='waitress', workers=3, clear_untrusted_proxy_headers=True)
#        app.run(debug="True", host="0.0.0.0", port='8086', reloader=True, server='gunicorn', workers=3, daemon=True)
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
