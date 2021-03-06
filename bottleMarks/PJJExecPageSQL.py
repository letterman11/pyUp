from marks import *
from SQLStrings import *
from error import *
from lib.util import *
import globals as g
from globals import *
import sqlite3
import re
############################################
## Bottle Modified ExecPageSQL function #### 
## PJJExecPageSQL                       ####
## standalone CGI function to be required ##
############################################
def exec_page(req,user_id,user_name,errObj):
    tabMap = g.tabMap
    print user_id + "Req Cookie  ID"
    searchboxTitle = unWrap(req,'searchbox')
    searchTypeBool = unWrap(req,'searchtype')
    tabtype = unWrap(req,'tab') or tabMap['tab_DATE']
    tabtype = int(tabtype)
    sort_crit = unWrap(req,'sortCrit') 
    if sort_crit != None and sort_crit != 'undefined':
        sort_crit = int(sort_crit)

    searchboxURL = unWrap(req,'searchbox2')
    ORDER_BY_CRIT = ""
    sort_asc = 0
    sort_desc = 1
    sort_date_asc = 2
    sort_date_desc = 3
    storedSQLStr = ""
    sort_ord  = "" 
    exec_sql_str = ""
    print str(searchboxTitle)   + " searchBox"
    print str(searchTypeBool)  + " searchBool"

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
    if searchTypeBool == "COMBO" and (isset(searchboxTitle)) and (isset(searchboxURL)):
        #exit
        queri = re.split("\s+",searchboxTitle)
        if len(queri) < 2:
            qstr = " a.title like \"%" + searchboxTitle + "%\"  and b.url like '%" + searchboxURL + "%' "# sort_ord
            exec_sql_str = main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        else:
            qstr = " a.title like \"%" + queri[0] + "%\" "
            for q in queri[1:]:
                if searchTypeBool == "OR":
                    qstr += " or a.title like \"%" + q + "%\" " 
                else:
                    qstr += " and a.title like \"%" + q + "%\" " 
        ###########################################
        # added two lines below to include url in search save and commented out the replaced line which only had the regular title search terms 
        ##########################################
        qstr +=  " and b.url like '%" + searchboxURL + "%' " 
        exec_sql_str = main_sql_str + qstr + ORDER_BY_DATE +  ' desc ' #sort_ord
        ##########################################
        #exec_sql_str = main_sql_str + qstr  + " and b.url like '%" + searchboxURL + "%' " + ORDER_BY_DATE +  ' desc ' #sort_ord
        storedSQLStr = main_sql_str + qstr 
        storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif isset(searchboxTitle):
        print "Hit search" + searchboxTitle
          #ORDER_BY_CRIT 
        queri = re.split("\s*",searchboxTitle)
        if len(queri) < 2:
            #qstr = " a.title like '%" + searchboxTitle + "%' "# sort_ord
            qstr = " a.title like \"%" + searchboxTitle + "%\" "# sort_ord
            exec_sql_str = main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        else:
            qstr = " a.title like \"%" + queri[0] + "%\" "
            for q in queri[1:]:
                if searchTypeBool == "AND":
                    qstr += " and a.title like \"%" + q + "%\" " 
                else:  
                    qstr += " or a.title like \"%" + q + "%\" " 
        exec_sql_str = main_sql_str + qstr  + ORDER_BY_DATE +  ' desc ' #sort_ord
        storedSQLStr = main_sql_str + qstr 
        storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif isset(searchboxURL):
        qstr = " b.url like '%" + searchboxURL + "%' "# sort_ord
        exec_sql_str = main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        storedSQLStr = main_sql_str + qstr 
        storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
##############################################################################################
# End of logic branches for SrcBoxTitle + SrchBoxURL + Radio Button
##############################################################################################
    else:
##############################
##for entry of tabs
#############################
        if tabtype == tabMap['tab_AE']:
            exec_sql_str = main_sql_str + AE_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_FJ']:
            exec_sql_str = main_sql_str + FJ_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_KP']:
            exec_sql_str = main_sql_str + KP_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_QU']:
            exec_sql_str = main_sql_str + QU_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_VZ']:
            exec_sql_str = main_sql_str + VZ_str + ORDER_BY_CRIT + sort_ord
        elif tabtype == tabMap['tab_DATE']:
            exec_sql_str = date_sql_str + sort_ord + "limit 200 "
        elif tabtype == tabMap['tab_SRCH_TITLE']:
            storedSQLStr = getStoredSQL(req)
            exec_sql_str = storedSQLStr + ORDER_BY_CRIT + sort_ord
###################################
##################################
    executed_sql_str =  exec_sql_str if (tabtype != tabMap['tab_DATE']) else date_sql_str + sort_ord + " limit 200 "
##########
# Start of Execution of SQL
#########
    tabMap = {y:x for x,y in tabMap.iteritems()}
    print sort_crit
    print "Exec webMark SQL " + executed_sql_str
    print str(tabtype) + " tab in play"
#    conn = sqlite3.connect(g.connFile)
    conn = sqlite3.connect(connFile)
    #conn.text_factory = bytes
    conn.text_factory = lambda x: x.decode("latin1")
    try:
        curs = conn.cursor()
        curs.execute(executed_sql_str, (user_id,))
        dbRows =curs.fetchall()
        print "RowCountWB " + str(len(dbRows))
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
        print string + " !RED"
        return False 
    elif string == None:
        print str(string) + " REDDER"
        return False
    elif re.match(r"\s+$", string):
        return False
    else:
        print str(string) + str(len(string)) + "TRUE?"
        return True 

def unWrap(req,reqObj):
    try:
        parmval = req.params[reqObj]
    except:
        return None
    return parmval 

