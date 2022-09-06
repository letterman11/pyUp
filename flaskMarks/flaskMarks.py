from flask import Flask, render_template, request, session
from datetime import datetime
from marks import Marks
from functools import wraps
from PJJExecPageSQL import exec_page
import lib.util as util 
import time
import connection_factory as db
from globals import *
from error import *
import re
import uuid



app = Flask(__name__)

app_cookie_path="/flaskMarks"

################################################################
# randomly generate secret key -- keep out of this file or other
# below is just for testing... and should be taken out!!!!
#################################################################

rnd_secret_key = uuid.uuid4().hex
app.secret_key = rnd_secret_key

place = db.db_factory().place

# static files ############################################
# served by Flask  local static dir-- 
# ideally would be served by static server like Apache or Nginx
###########################################################

### decorator functions
#must alter authenticate for Flask to use their session module 
# Not using sessions yet
###
def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        aa = [ (k) for k in request.form]
        print ("Here")
        print(aa, "")
        #print(request.form['searchtype'])
        if validate_session(session) == False:
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

@app.route("/flaskMarks/registration")
@app.route('/registration')
def register():
    return Marks().renderRegistrationView()


@app.post("/flaskMarks/regAuth")
@app.post('/regAuth')
def registerAuth():

    try:
        user_name = request.form['user_name']
        user_pass1  = request.form['new_user_pass1']
        user_pass2  = request.form['new_user_pass2']
        email_address  = request.form['email_address']

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
    
    
    insert_sql_str = "INSERT INTO WM_USER (USER_ID,USER_NAME,USER_PASSWD,EMAIL_ADDRESS) VALUES ({},{},{},{})".format(place,place,place,place)

    try:
        curs.execute(insert_sql_str, (user_id, user_name, user_pass1, email_address,))
    except Exception:
        print ("Insert Error Error Error wm_user")
        return Marks().renderRegistrationView(Error(2000).errText())
    else:
        conn.commit()
    finally:
        conn.close()

    return Marks().renderDefaultView("grey", "Successfully Registered " + user_name)

@app.route("/flaskMarks/default")
@app.route('/default')
def logIn():
    return Marks().renderDefaultView()
    #return renderDefaultView()

##################################################################
###  --  Authenticated routes -- via authenticate decorator -- ###
##################################################################

@app.route("/flaskMarks")
@app.route("/")
@authenticate
def index():
    return renderMainView()

@app.route("/flaskMarks/webMarks")
@app.route("/webMarks")
@authenticate
def indexWB():
    return renderMainView()

@app.route("/flaskMarks/tabView")
@app.route("/tabView")
@authenticate
def indexView():
    return renderMainView()

@app.route("/flaskMarks/searchMark", methods=['POST'])
@app.route("/searchMark", methods=['POST'])
@authenticate
def searchWebMark():
    return renderMainView()

@app.route("/flaskMarks/insertMark", methods=['POST'] )
@app.route("/insertMark", methods=['POST'])
@authenticate
def addWebMark():
    user_id = session['wmUserID']	
    title = request.form['mark_title']	
    url = request.form['mark_url']	
    #time.daylight

    if not util.isset(title) or not util.isset(url):
        return renderMainView(user_id,Error(151))

    #unix_epochs = int(time.time()) - time.timezone
    unix_epochs = int(time.time())

    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    dateAdded = unix_epochs * (1000 * 1000)
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

    tbl1MaxId +=1
    tbl2MaxId +=1

    curs.execute("select b.url from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = {} and b.URL =  {} ".format(place,place), (user_id, url))
    dup_check = curs.fetchone()
    
    if dup_check:
        print ("Duplicate")
        return renderMainView(user_id,Error(150))
    
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
        print ("Insert Error Error wmbookmark")
        conn.rollback()
        return renderMainView(user_id,Error(2000))
    else:
        conn.commit()
    finally:
        conn.close()
      
    return renderMainView()

@app.post("/flaskMarks/updateMark")
@app.post("/updateMark")
@authenticate
def updateMark():

    user_id = session['wmUserID']

    title = request.form['title_update']	
    
    url = request.form['url_update']	
    
    tblBookMarkId = request.form['bk_id']	
     
    print (tblBookMarkId)
 
    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    dateAdded = unix_epochs * (1000 * 1000)

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

@app.post("/flaskMarks/deleteMark")
@app.post("/deleteMark")
@authenticate
def deleteMark():
    
    user_id = session['wmUserID']
    tblBookMarkId = request.form['bk_id']
    
    print (tblBookMarkId)

    unix_epochs = int(time.time())
    #use antique mozilla time format (1000 * 1000) unix epoch seconds => microseconds 
    dateAdded = unix_epochs * (1000 * 1000)
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

@app.route("/flaskMarks/deltaPass", methods=['POST'])
@app.route("/deltaPass", methods=['POST'])
@authenticate
def deltaPass():
    
    try:
        (user_id,user_name,user_pass) = pre_auth()
    except:
        return renderMainView(request.form['user_name'],Error(112))
   
    new_passwd = request.form['user_pass']

    if not user_id:
        return renderMainView(Error(user_id,112))
    else:
        try:
            conn = db.db_factory().connect()
            curs = conn.cursor()
            place = db.db_factory.place
            curs.execute("update WM_USER set USER_PASSWD = {}  where USER_NAME = {} ".format(place,place), (new_passwd,user_name));

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

@app.route("/flaskMarks/logout")
@app.route("/logout")
def logOut():
    session.clear()
    return Marks().renderDefaultView()

@app.route("/flaskMarks/authenCred", methods=['POST'])
@app.route("/authenCred", methods=['POST'])
def authenCredFunc():
     
    (user_id,user_name,user_pass) = pre_auth() or (None,None,None)

    if user_id:
        authorize(user_id,user_name)

    else:
        return Marks().renderDefaultView(colorStyle="red",displayText="Incorrect User ID/Password")

    return renderMainView(user_id)

def validate_session(session):
   
    try:

       wmSID = session['wmSessionID']
       userID = session['wmUserID']

    except:

        return False
    
    return util.validateSession2(session) 


def authorize(user_id,user_name):

    sessionID = util.genSessionID()
    
    session['wmSessionID'] = sessionID
    session['wmUserID'] = user_id
    session['wmUserName'] = user_name
    session['expires'] = None
    session['domain'] = None

    util.saveSession(sessionID)

def renderMainView(user_id=None,errObj=None):
#   user_name=None
#
#    try:
#
#        user_name = request.form['user_name']
#   except:
#
#        pass
#    if not user_id or not user_name:
    user_id = session['wmUserID']
    user_name = session['wmUserName']

    return exec_page(request,session,user_id,user_name,errObj)
    #return exec_page(request,user_id,user_name,errObj)

if __name__ ==  '__main__':
    app.run(debug="True", host="0.0.0.0", port='8090', reloader=True, server='waitress', workers=3)
    #app.run(debug="True", host="0.0.0.0", port='5000')
    #app.run(debug="True", host="0.0.0.0", port='8086', reloader=True, server='gunicorn', workers=3)
