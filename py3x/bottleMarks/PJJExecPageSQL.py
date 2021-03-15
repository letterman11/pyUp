from marks import *
from SQLStrings import *
from error import *
import lib.util as util
import globals as g
from globals import *
#import sqlite3
import connection_factory as db
import re
############################################
## Bottle Modified ExecPageSQL function #### 
## PJJExecPageSQL                       ####
## standalone CGI function to be required ##
############################################
def exec_page(req,user_id,user_name,errObj):
    tabMap = g.tabMap
    print (user_id + "Req Cookie  ID")

    searchBoxTitle = unWrap(req,'searchBoxTitle')
    searchTypeBool = unWrap(req,'searchtype')

    searchDateStart = unWrap(req,'searchDateStart')
    searchDateEnd = unWrap(req,'searchDateEnd')

    tabtype = unWrap(req,'tab') or tabMap['tab_DATE']
    tabtype = int(tabtype)
    sort_crit = unWrap(req,'sortCrit') 
    if sort_crit != None and sort_crit != 'undefined':
        sort_crit = int(sort_crit)

    searchBoxURL = unWrap(req,'searchBoxURL')
    ORDER_BY_CRIT = ""
    sort_asc = 0
    sort_desc = 1
    sort_date_asc = 2
    sort_date_desc = 3
    storedSQLStr = ""
    sort_ord  = "" 
    exec_sql_str = ""
    print (str(searchBoxTitle)   + " searchBoxTitle")
    print (str(searchTypeBool)  + " searchBool")


    tabMap2 = {y:x for x,y in tabMap.items()}


    #temporary code
    if util.isset(searchDateStart):
        print(searchDateStart)
        res_start_1 = re.match(r'([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{4})|([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})',searchDateStart)
#        res_start_2 = re.match(r'([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})',searchDateStart)

        if not res_start_1:
            marks = Marks(tabMap2[tabtype],None,None,Error(151))
            return marks.renderMainView(user_id,sort_crit,tabMap)
   
    if util.isset(searchDateEnd):

        res_end_1 = re.match(r'([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{4})|([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})',searchDateEnd)
#        res_end_2 = re.match(r'([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})',searchDateEnd)

        if not res_end_1:
            marks = Marks(tabMap2[tabtype],None,None,Error(151))
            return marks.renderMainView(user_id,sort_crit,tabMap)


    conn = db.db_factory().connect()

    g_main_sql_str = main_sql_str.format(db.db_factory.place)
    g_date_sql_str = date_sql_str.format(db.db_factory.place)

#############################################################################
#Sort Criteria setting of ORDER_BY_CRITERIA
#############################################################################
    if sort_crit == 0:
        ORDER_BY_CRIT = ORDER_BY_TITLE
        sort_ord = ' asc '    
    elif sort_crit == 1:
        ORDER_BY_CRIT = ORDER_BY_TITLE
        sort_ord = ' desc '
    elif sort_crit == 2:
        ORDER_BY_CRIT = ORDER_BY_DATE
        sort_ord = ' asc '
    else:
        ORDER_BY_CRIT = ORDER_BY_DATE
        sort_ord = ' desc '
#############################################################################
#############################################################################
##########################################################
# SearchBoxTitle + SearchBoxURL + AND/OR Radio Button
##########################################################
    if searchTypeBool == "COMBO" and (isset(searchBoxTitle)) and (isset(searchBoxURL)):
        queri = re.split("\s+",searchBoxTitle)
        if len(queri) < 2:
            qstr = " a.title like \"%" + re.sub(r'^s','S',searchBoxTitle) + "%\"  and b.url like '%" + re.sub(r'^s','S',searchBoxURL) + "%' "# sort_ord
            exec_sql_str = g_main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        else:
            qstr = " a.title like \"%" + re.sub(r'^s','S',queri[0]) + "%\" "
            for q in queri[1:]:
                if searchTypeBool == "OR":
                    qstr += " or a.title like \"%" + re.sub(r'^s','S',q) + "%\" " 
                else:
                    qstr += " and a.title like \"%" + re.sub(r'^s','S',q) + "%\" " 
        ###########################################
        # added two lines below to include url in search save and commented out the replaced line which only had the regular title search terms 
        ##########################################
        qstr +=  " and b.url like '%" + searchBoxURL + "%' " 
        exec_sql_str = g_main_sql_str + qstr + ORDER_BY_DATE +  ' desc ' #sort_ord
        ##########################################
        #exec_sql_str = g_main_sql_str + qstr  + " and b.url like '%" + searchBoxURL + "%' " + ORDER_BY_DATE +  ' desc ' #sort_ord
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif isset(searchBoxTitle):
        print ("Hit search" + searchBoxTitle)
          #ORDER_BY_CRIT 
        #queri = re.split("\s*",searchBoxTitle)
        queri = re.split("\s+",searchBoxTitle)
        if len(queri) < 2:
            qstr = " a.title like \"%" + re.sub(r'^s','S',searchBoxTitle) + "%\" "# sort_ord
            exec_sql_str = g_main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        else:
            qstr = " a.title like \"%" +   re.sub(r'^s','S',queri[0])+ "%\" "
            for q in queri[1:]:
                if searchTypeBool == "AND":
                    qstr += " and a.title like \"%" +  re.sub(r'^s','S',q) + "%\" " 
                else:  
                    qstr += " or a.title like \"%" +  re.sub(r'^s','S',q) + "%\" " 
        exec_sql_str = g_main_sql_str + qstr  + ORDER_BY_DATE +  ' desc ' #sort_ord
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif isset(searchBoxURL):
        qstr = " b.url like '%" + re.sub(r'^s','S',searchBoxURL) + "%' "# sort_ord
        exec_sql_str = g_main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif isset(searchDateStart) and isset(searchDateEnd):
        qstr =  " dateAdded between " + str(util.convertDateEpoch(searchDateStart)) + " and " + str(util.convertDateEpoch(searchDateEnd))
        exec_sql_str = g_main_sql_str + qstr + " ) "
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_DATE']
    elif isset(searchDateStart):
        dateAddedEnd =  int(((util.convertDateEpoch(searchDateStart) / (1000 * 1000)) + (60 * 60 * 24)) * (1000 * 1000) ) 
        qstr =  " dateAdded between " + str(util.convertDateEpoch(searchDateStart)) + " and " + str(dateAddedEnd)
        exec_sql_str = g_main_sql_str + qstr + " ) "
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_DATE']
##############################################################################################
# End of logic branches for SrcBoxTitle + SrchBoxURL + Radio Button
##############################################################################################
    else:
##############################
##for entry of tabs
#############################
        if tabtype == tabMap['tab_AE']:
            exec_sql_str = g_main_sql_str + AE_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_FJ']:
            exec_sql_str = g_main_sql_str + FJ_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_KP']:
            exec_sql_str = g_main_sql_str + KP_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_QU']:
            exec_sql_str = g_main_sql_str + QU_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_VZ']:
            exec_sql_str = g_main_sql_str + VZ_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_DATE']:
            exec_sql_str = g_date_sql_str + sort_ord + "limit 200 "
        elif tabtype == tabMap['tab_SRCH_TITLE']:
            storedSQLStr = util.getStoredSQL(req)
            if not storedSQLStr:
                exec_sql_str = g_date_sql_str + sort_ord + "limit 200 "
            else:
                exec_sql_str = storedSQLStr + ORDER_BY_CRIT + sort_ord
###################################
##################################
    executed_sql_str =  exec_sql_str if (tabtype != tabMap['tab_DATE']) else g_date_sql_str + sort_ord + " limit 200 "
##########
# Start of Execution of SQL
#########
    #tabMap = {y:x for x,y in tabMap.iteritems()}
    tabMap = {y:x for x,y in tabMap.items()}
    print (sort_crit)
    print ("Exec webMark SQL " + executed_sql_str)
    print (str(tabtype) + " tab in play")
    #conn = sqlite3.connect(connFile)
    conn = db.db_factory().connect()
    #conn.text_factory = bytes
    conn.text_factory = lambda x: x.decode("latin1")
    try:
        curs = conn.cursor()
        curs.execute(executed_sql_str, (user_id,))
        dbRows =curs.fetchall()
        print ("RowCountWB " + str(len(dbRows)))
        conn.close()
    except Exception as inst:    
        print (inst)
        marks = Marks(tabMap[tabtype],None,None,Error(2000))
        #return marks.renderMainView(user_name,sort_crit,tabMap)
        return marks.renderMainView(user_id,sort_crit,tabMap)

    markObj = Marks(tabMap[tabtype],dbRows,len(dbRows),errObj)
    #return markObj.renderMainView(user_name,sort_crit,tabMap)
    return markObj.renderMainView(user_id,sort_crit,tabMap)
'''
try:
    with con:
        con.execute("insert into person(firstname) values (?)", ("Joe",))
except sqlite3.IntegrityError:
    print "couldn't add Joe twice"
'''
############
# End of SQL Execution
###########
def isset(string):
    if (string != None) and len(string) == 0:
        print (string + " !RED")
        return False 
    elif string == None:
        print (str(string) + " REDDER")
        return False
    elif re.match(r"\s+$", string):
        return False
    else:
        print (str(string) + str(len(string)) + "TRUE?")
        return True 

def unWrap(req,reqObj):
    try:
        parmval = req.params[reqObj]
    except:
        return None
    return parmval 


