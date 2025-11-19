from bottle import Bottle, run, route, request, response, static_file, error
from datetime import datetime
from marks import Marks
from functools import wraps
from PJJExecPageSQL import exec_page
#import lib.util as util 
import lib.util_db as util 
import time
import connection_factory as db
from globals import *
from error import *
import re

app = Bottle()  

app_cookie_path="/exWebMarks"
fiveDayExpire = int(time.time()) + 60 * 60 *24 *5
path = app_cookie_path

place = db.db_factory().place

# static files ############################################
# served by bottle -- ideally would be served by static 
# server like Apache or Nginx
@app.route('/public/css/<filename>')
@app.route('/static/css/<filename>')
def server_static_css(filename):
    return static_file(filename, root="./public/css")
     
@app.route('/public/images/<filename>')
@app.route('/static/images/<filename>')
def server_static_imgs(filename):
    return static_file(filename, root="./public/images")

@app.route('/public/js/<filename>')
@app.route('/static/js/<filename>')
def server_static_js(filename):
    return static_file(filename, root="./public/js")
###########################################################


### decorator functions
def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        #if validate_session() == False:
        aa = [ (k,v) for k,v in request.forms.allitems()]
        print( aa )
        if validate_session2(request) == False:
            return Marks().renderDefaultView()
        return f(*args, **kwargs)
    return wrapper


def pre_auth(): 
    
    usr_name = util.unWrap(request, 'user_name') 
    usr_pass = util.unWrap(request, 'user_pass')
    old_usr_pass = util.unWrap(request, 'old_user_pass')
    
    exec_sql_str = str()

    if old_usr_pass: # for update
        exec_sql_str = "select user_id, user_name, user_passwd from WM_USER where user_passwd = '" + old_usr_pass +  "' and user_name ='"  + usr_name + "' "
    else:
        exec_sql_str = "select user_id, user_name, user_passwd from WM_USER where user_passwd = '" + usr_pass + "' and user_name ='" + usr_name  + "' "

    ### error checking ????? ##############
    conn = db.db_factory().connect()
    curs = conn.cursor()
    curs.execute(exec_sql_str)
    user_row = curs.fetchall()
    conn.close()
	
    if user_row:
        user_row= user_row[0]
        print (user_row)
        print ("user row list above")
        usr_id,usr_name,usr_pass = user_row[0],user_row[1],user_row[2]
       
        return (usr_id,usr_name,usr_pass)

    else:
        return None
        
def pre_auth2():
    
    usr_name = util.unWrap(request, 'user_name') 
    usr_pass = util.unWrap(request, 'user_pass')
    old_usr_pass = util.unWrap(request, 'old_user_pass')

    if not usr_name or not usr_pass:
        return None;
    
    password_digest = util.digest_pass(usr_pass);
    password_old_digest = util.digest_pass(old_usr_pass);
        
    exec_sql_str = "select user_id, user_name, user_passwd from WM_USER where user_name = '" + usr_name + "' ";
    
    ### error checking ????? ##############

    conn = db.db_factory().connect()
    curs = conn.cursor()
    curs.execute(exec_sql_str)
    
    db_row = curs.fetchall()

    conn.close()
    
    if db_row:
        print (db_row)
        (db_usr_id, db_usr_name, db_usr_pass) = db_row.pop()
    else:
        return None
              
   
    if(util.isset(old_usr_pass) and (db_usr_pass == old_usr_pass) or db_usr_pass == password_old_digest):
         
        return (db_usr_id, db_usr_name, usr_pass); 
    
    elif ((db_usr_pass == usr_pass) or (db_usr_pass == password_digest)):
    
        return (db_usr_id, db_usr_name, db_usr_pass) 
    
    else:
        return None
    

@app.route("/exWebMarks/registration")
@app.route('/registration')
def register():
    return Marks().renderRegistrationView()


@app.post("/exWebMarks/regAuth")
@app.post('/regAuth')
def registerAuth():

    try:
        user_name = request.params['user_name']
        user_pass1 = request.params['new_user_pass1']
        user_pass2 = request.params['new_user_pass2']
        email_address = request.params['email_address']

    except KeyError:
        return Marks().renderRegistrationView(Error(112).errText()) 
         

    if (re.match(r'^$',user_name) or re.match(r'^$',user_pass1) or re.match(r'^$',user_pass2)):
        return Marks().renderRegistrationView(Error(107).errText()) 
    
    if (user_pass1 !=  user_pass2):
        return Marks().renderRegistrationView(Error(113).errText()) 

    if len(user_pass1) < 6:
        return Marks().renderRegistrationView(Error(111).errText())

    if not re.match(r"^[a-zA-z0-9\.]+\@[a-zA-Z0-9\.]+",email_address):
        return Marks().renderRegistrationView(Error(119).errText())
   

    ##########################################################    

    part_id = util.genSessionID()
    user_id = user_name[0:5]
    part_id = part_id[0:5]

    user_id = user_id+"_"+part_id

    ########################################
    conn = db.db_factory().connect()
    curs = conn.cursor()
    place = db.db_factory.place
    ########################################

    hash_pass = util.digest_pass(user_pass1)
    
    insert_sql_str = "INSERT INTO WM_USER (USER_ID,USER_NAME,USER_PASSWD,EMAIL_ADDRESS) VALUES ({},{},{},{})".format(place,place,place,place)
    
    try:
        #curs.execute(insert_sql_str, (user_id, user_name, user_pass1, email_address,))
        curs.execute(insert_sql_str, (user_id, user_name, hash_pass, email_address,))
    except Exception:
        print ("Insert Error Error Error wm_user")
        return Marks().renderRegistrationView(Error(120).errText())
    else:
        conn.commit()
    finally:
        conn.close()

    return Marks().renderDefaultView("red", "Successfully Registered " + user_name)

@app.route("/exWebMarks/default")
@app.route('/default')
def logIn():
    return Marks().renderDefaultView()
    #return renderDefaultView()

@app.error(404)
def error404(error):
    return renderErrorPageView()



##################################################################
###  --  Authenticated routes -- via authenticate decorator -- ###
##################################################################

@app.route("/exWebMarks")
@app.route("/")
@authenticate
def index():
    return renderMainView()

@app.route("/exWebMarks/webMarks")
@app.route("/webMarks")
@authenticate
def indexWB():
    return renderMainView()

@app.route("/exWebMarks/tabView")
@app.route("/tabView")
@authenticate
def indexView():
    return renderMainView()

@app.route("/exWebMarks/tabTableView")
@app.route("/tabTableView")
@authenticate
def tabTableView():
    return renderTabTableView()

@app.post("/exWebMarks/searchMark")
@app.post("/searchMark")
@authenticate
def searchWebMark():
    return renderMainView(init=False)
    #return renderTabTableView()
    
@app.post("/exWebMarks/insertMark")
@app.post("/insertMark")
@authenticate
def addWebMark():
    user_id = request.get_cookie('wmUserID')	

    #utf-8 decoded-presented bottle forms post version
    title = request.forms.mark_title
    #utf-8 decoded-presented bottle forms post version
    url = request.forms.mark_url

    #time.daylight

    if not util.isset(title) or not util.isset(url):
        return renderMainView(user_id,Error(151))

    #unix_epochs = int(time.time()) - time.timezone
    unix_epochs = int(time.time())

    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    #delete of mozilla microseconds
    #----------------------------------
    #dateAdded = unix_epochs * (1000 * 1000)

    dateAdded = unix_epochs 

    date_Added = unix_epochs # for new datetime column
    (year, mon, day, hour, mins, secs)  = time.localtime(date_Added)[0:6]
    date_Added = ('{}-{}-{} {}:{}:{}').format(year,mon,day,hour,mins,secs)


    conn = db.db_factory().connect()
    curs = conn.cursor()
    place = db.db_factory.place

    curs.execute("select max(BOOKMARK_ID) from WM_BOOKMARK")
    (tbl1MaxId,) = curs.fetchone()
    curs.execute("select max(PLACE_ID) from WM_PLACE")
    (tbl2MaxId,) = curs.fetchone()

    print (tbl1MaxId)
    print (tbl2MaxId)

    if not tbl1MaxId:
        tbl1MaxId = 0

    if not tbl2MaxId:
        tbl2MaxId = 0

    tbl1MaxId +=1
    tbl2MaxId +=1

    curs.execute("select b.url from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = {} and b.URL =  {} ".format(place,place), (user_id, url))
    dup_check = curs.fetchone()
    
    if dup_check:
        print ("Duplicate")
        response.set_cookie("Error", str(150), path=path, expires=fiveDayExpire)
        response.set_cookie("Error_url", str(url), path=path, expires=fiveDayExpire)
        return renderMainView(user_id,Error(150, url))
#        return renderTabTableView(user_id,Error(150))
    
    try:
        curs.execute("insert into WM_PLACE (PLACE_ID, URL, TITLE) values ({},{},{})".format(place,place,place), (tbl2MaxId, url, title,))
    except:
        print ("Insert Error wmplace")
        conn.rollback()
        return renderMainView(user_id,Error(2000))

    try:
        curs.execute("insert into WM_BOOKMARK (BOOKMARK_ID, USER_ID, PLACE_ID, TITLE, DATEADDED, DATE_ADDED) values ({},{},{},{},{},{})".format(place
                                ,place,place,place,place,place), (tbl1MaxId, user_id, tbl2MaxId, title, dateAdded, date_Added,))
    except:
        print ("Insert Error wmbookmark")
        conn.rollback()
        return renderMainView(user_id,Error(2000))
    else:
        conn.commit()
    finally:
        conn.close()
      
    return renderMainView()

@app.post("/exWebMarks/updateMark")
@app.post("/updateMark")
@authenticate
def updateMark():

    user_id = request.get_cookie('PYwmUserID')	

    #utf-8 decoded-presented bottle forms post version
    title = request.forms.title_update
    #utf-8 decoded-presented bottle forms post version
    url = request.forms.url_update


    tblBookMarkId = request.params['bk_id']
    print (tblBookMarkId)
 
    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 

    #dateAdded = unix_epochs * (1000 * 1000)
    dateAdded = unix_epochs 

    conn = db.db_factory().connect()
    curs = conn.cursor()

    try:
        curs.execute("select PLACE_ID from WM_BOOKMARK where BOOKMARK_ID = {} ".format(place) , (tblBookMarkId,))

    except Exception as ex:
        print ("error execute update")
        raise ex
        return renderMainView(user_id,Error(153))

    (tblPlaceId,) = curs.fetchone()
    print ("PlaceID " + str(tblPlaceId))

    try:
        curs.execute("update WM_BOOKMARK set TITLE = {} where BOOKMARK_ID = {} ".format(place,place), (title, tblBookMarkId,))
        curs.execute("update WM_PLACE set  URL = {} , TITLE = {} where PLACE_ID = {} ".format(place,place,place), (url, title,tblPlaceId,))
    except Exception as ex:
        raise ex
        return renderMainView(user_id,Error(153))
    else:
        conn.commit()
    finally:
        conn.close()
 
    return renderMainView()


@app.post("/exWebMarks/deleteMark")
@app.post("/deleteMark")
@authenticate
def deleteMark():
    user_id = request.get_cookie('wmUserID')
    tblBookMarkId = request.params['bk_id']
    print (tblBookMarkId)

    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 

    #dateAdded = unix_epochs * (1000 * 1000)
    dateAdded = unix_epochs

    conn = db.db_factory().connect()
    curs = conn.cursor()

    try:
        curs.execute("select PLACE_ID from WM_BOOKMARK where BOOKMARK_ID = {} ".format(place), (tblBookMarkId,))

    except Exception as ex:
        print ("error execute select in deleteMark")
        raise ex
        return renderMainView(user_id,Error(153))

    (tblPlaceId,) = curs.fetchone()
    print ("PlaceID " + str(tblPlaceId))



    try:
        curs.execute("delete from  WM_PLACE  where PLACE_ID = {} ".format(place), (tblPlaceId,))
        curs.execute("delete from  WM_BOOKMARK  where BOOKMARK_ID = {} ".format(place),(tblBookMarkId,))

    except Exception as ex:
        print ("error execute delettion")
        raise ex
        return renderMainView(user_id,Error(153))

    else:
        conn.commit()
    finally:
        conn.close()
 
    return renderMainView()

@app.post("/exWebMarks/deltaPass")
@app.post("/deltaPass")
@authenticate
def deltaPass():
    
    try:
        #(user_id,user_name,user_pass) = pre_auth() or (None,None,None)
        (user_id,user_name,user_pass) = pre_auth2() or (None,None,None)
    except:
        return renderMainView(request.params['user_name'],Error(112))
   
    new_passwd = request.params['user_pass']

    new_hash_pass = util.digest_pass(new_passwd);


    if not user_id:
        return renderMainView(user_id,Error(112))
    else:
        try:
            conn = db.db_factory().connect()
            curs = conn.cursor()
            place = db.db_factory.place
            #curs.execute("update WM_USER set USER_PASSWD = {}  where USER_NAME = {} ".format(place,place), (new_passwd,user_name));
            curs.execute("update WM_USER set USER_PASSWD = {}  where USER_NAME = {} ".format(place,place), (new_hash_pass,user_name));
        except:
            return renderMainView(user_id,Error(102))
        else:
            conn.commit()
        finally:
            conn.close()
    return renderMainView()

######################################################################
## end authenticated routes via decorator ############################
######################################################################

@app.route("/exWebMarks/logout")
@app.route("/logout")
def logOut():
    return Marks().renderDefaultView()

@app.route("/exWebMarks/authenCred", method=['GET', 'POST'])
@app.route("/authenCred", method=['GET', 'POST'])
def authenCredFunc():

    #(user_id,user_name,user_pass) = pre_auth() or (None,None,None)
    (user_id,user_name,user_pass) = pre_auth2() or (None,None,None)

    if user_id:
        authorize(user_id,user_name)
    else:
        return Marks().renderDefaultView(colorStyle="red",displayText=Error(112).errText())
    
    return renderMainView(user_id)

def validate_session():
    wmSID = request.get_cookie('wmSessionID')
    user_id = request.get_cookie('wmUserID')
    if not wmSID:
        return False

def validate_session2(req):
#    return util.validateSession2(req) 
    return util.validateSessionDB(req) 

def authorize(user_id,user_name):
    sessionID = util.genSessionID()
    init_count = 0

    fiveDayExpire = int(time.time()) + 60 * 60 *24 *5
    
    path = app_cookie_path    
    response.set_cookie('wmSessionID',str(sessionID), path=path, expires=fiveDayExpire)
    response.set_cookie('wmUserID',str(user_id), path=path, expires=fiveDayExpire)
    response.set_cookie('wmUserName', str(user_name), path=path, expires=fiveDayExpire)
    response.set_cookie('Counter', str(init_count), path=path, expires=fiveDayExpire)
    print(str(user_id) , " USERID")
    
    #util.saveSession(sessionID)
    util.saveSessionDB(sessionID,user_id)
#   response.set_cookie('expires', 60*60)

def renderMainView(user_id=None,errObj=None,init=True):
    user_name=None
    try:
        user_name = request.params['user_name']
    except:
        pass
    if not user_id or not user_name:
        user_id = request.get_cookie('wmUserID')
        user_name = request.get_cookie('wmUserName')

    return exec_page(request,user_id,user_name,errObj,init)

def renderTabTableView(user_id=None,errObj=None,init=False):    
    user_name=None
    try:
        user_name = request.params['user_name']
    except:
        pass
    print ("tabFunction")
    if not user_id or not user_name:
        user_id = request.get_cookie('wmUserID')
        user_name = request.get_cookie('wmUserName')
    
    error   = request.get_cookie("Error")
    err_url = request.get_cookie("Error_url")
    
    if error:
        errObj = Error(int(error), err_url)
    else:
        errObj = None
    response.delete_cookie("Error")    
    response.delete_cookie("Error_url")    
    return exec_page(request,user_id,user_name,errObj,init)
    
    
def renderErrorPageView():
          return Marks().renderErrorPageView()

if __name__ ==  '__main__':
#        app.run(debug=True, host="0.0.0.0", port='8070', reloader=True, server='waitress', workers=3)
#        app.run(debug=True, host="0.0.0.0", port='8092', reloader=True, server='waitress', workers=3)
        app.run(daemon=False, debug=False, host="0.0.0.0", port='8088', reloader=True, server='gunicorn', workers=3)
