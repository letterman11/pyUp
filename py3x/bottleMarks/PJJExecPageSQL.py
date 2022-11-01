from marks import *
from SQLStrings import *
from error import *
import lib.util as util
import globals as g
from globals import *
import connection_factory as db
import re
############################################
## Bottle Modified ExecPageSQL function #### 
## PJJExecPageSQL                       ####
## standalone CGI function to be required ##
############################################
def exec_page(req,user_id,user_name,errObj,sessionID,init):
    tabMap = g.tabMap
    print (user_id + " Req Cookie  IDs")

    searchBoxTitle = util.unWrap(req,'searchBoxTitle')
    searchTypeBool = util.unWrap(req,'searchtype')
    
    searchTypeBool = searchTypeBool or "AND";


    searchDateStart = util.unWrap(req,'searchDateStart')
    searchDateEnd = util.unWrap(req,'searchDateEnd')
    

    tabtype = util.unWrap(req,'tab') or tabMap['tab_DATE']
    tabtype = int(tabtype)
    print ("tab " + str(tabtype))
    sort_crit = util.unWrap(req,'sortCrit') 
    if sort_crit != None and sort_crit != 'undefined':
        sort_crit = int(sort_crit)

    searchBoxURL = util.unWrap(req,'searchBoxURL')
    ORDER_BY_CRIT = ""
    sort_asc = 0
    sort_desc = 1
    sort_date_asc = 2
    sort_date_desc = 3
    storedSQLStr = ""
    sort_ord  = "" 
    exec_sql_str = ""
    print (str(searchBoxTitle)   + " PJJ searchBoxTitle")
    print (str(searchTypeBool)  + " searchBool")


    tabMap2 = {y:x for x,y in tabMap.items()}

    multiDate = r'(([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{4}))|(([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2}))|(\b([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{2})\b)'
    shortDate = r'\b([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{2})\b'

    regMultiDate = re.compile(multiDate)
    regShortDate = re.compile(shortDate)

    #temporary code
    if util.isset(searchDateStart):
        res_start_1 = re.match(regMultiDate,searchDateStart)

        if not res_start_1:
            marks = Marks(tabMap2[tabtype],None,None,Error(151))
            return marks.renderMainView(user_id,sort_crit,tabMap)

        res_sub_1 = re.match(regShortDate,searchDateStart)
        if res_sub_1:
            searchDateStart = res_sub_1.group(1) + "-" + res_sub_1.group(2) + "-" + "20" +res_sub_1.group(3)
   
    if util.isset(searchDateEnd):

        res_end_1 = re.match(regMultiDate,searchDateEnd)

        if not res_end_1:
            marks = Marks(tabMap2[tabtype],None,None,Error(151))
            return marks.renderMainView(user_id,sort_crit,tabMap)

        res_sub_1 = re.match(regShortDate,searchDateEnd)
        if res_sub_1:
            searchDateEnd = res_sub_1.group(1) + "-" + res_sub_1.group(2) + "-" + "20" +res_sub_1.group(3)
   

    conn = db.db_factory()
    #g_main_sql_str = main_sql_str.format(db.db_factory.place)
    #g_date_sql_str = date_sql_str.format(db.db_factory.place)

    g_main_sql_str = main_sql_str_pg_index.format(db.db_factory.place) # Now intermediary index query
    g_date_sql_str = date_sql_str_pg_index.format(db.db_factory.place) # Now intermediary index query


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
    if searchTypeBool == "COMBO" and (util.isset(searchBoxTitle)) and (util.isset(searchBoxURL)):
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
        if len(queri) >= 2:
            qstr +=  " and b.url like '%" + re.sub(r'^s', 'S', searchBoxURL) + "%' " 
        exec_sql_str = g_main_sql_str + qstr + ORDER_BY_DATE +  ' desc ' #sort_ord
        ##########################################
        #exec_sql_str = g_main_sql_str + qstr  + " and b.url like '%" + searchBoxURL + "%' " + ORDER_BY_DATE +  ' desc ' #sort_ord
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif util.isset(searchBoxTitle):
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
    elif util.isset(searchBoxURL):
        qstr = " b.url like '%" + re.sub(r'^s','S',searchBoxURL) + "%' "# sort_ord
        exec_sql_str = g_main_sql_str + qstr + ORDER_BY_DATE  +' desc '  # sort_ord
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_TITLE']
    elif util.isset(searchDateStart) and util.isset(searchDateEnd) and (searchDateStart != searchDateEnd):
        dateAddedEnd =  int(((util.convertDateEpoch(searchDateEnd) / (1000 * 1000)) + (60 * 60 * 24)) * (1000 * 1000) ) 
        qstr =  "( dateAdded between " + str(util.convertDateEpoch(searchDateStart)) + " and " + str(dateAddedEnd)
        exec_sql_str = g_main_sql_str + qstr + " ) "
        storedSQLStr = g_main_sql_str + qstr 
        util.storeSQL(storedSQLStr,req)
        tabtype = tabMap['tab_SRCH_DATE']
    elif util.isset(searchDateStart):
        dateAddedEnd =  int(((util.convertDateEpoch(searchDateStart) / (1000 * 1000)) + (60 * 60 * 24)) * (1000 * 1000) ) 
        qstr =  " dateAdded between " + str(util.convertDateEpoch(searchDateStart)) + " and " + str(dateAddedEnd)
        exec_sql_str = g_main_sql_str + qstr 
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
            exec_sql_str = g_main_sql_str + " ( "  + AE_str + " ) " + ORDER_BY_CRIT + sort_ord 
        elif tabtype == tabMap['tab_FJ']:
            exec_sql_str = g_main_sql_str + " ( "  + FJ_str + " ) "+ ORDER_BY_CRIT + sort_ord 
        elif tabtype == tabMap['tab_KP']:
            exec_sql_str = g_main_sql_str + " ( "  + KP_str + " ) "+ ORDER_BY_CRIT + sort_ord 
        elif tabtype == tabMap['tab_QU']:
            exec_sql_str = g_main_sql_str + " ( "  + QU_str + " ) "+ ORDER_BY_CRIT + sort_ord 
        elif tabtype == tabMap['tab_VZ']:
            exec_sql_str = g_main_sql_str + " ( "  + VZ_str + " ) "+ ORDER_BY_CRIT + sort_ord 
        elif tabtype == tabMap['tab_DATE']:
            exec_sql_str = g_date_sql_str 
        elif tabtype == tabMap['tab_SRCH_TITLE']:
            storedSQLStr = util.getStoredSQL(req)
            if not storedSQLStr:
                exec_sql_str = g_date_sql_str + ORDER_BY_CRIT + sort_ord 
                exec_sql_str_page = date_sql_str_page
            else:
                exec_sql_str = storedSQLStr + ORDER_BY_CRIT + sort_ord 
###################################
##################################

    if tabtype != tabMap['tab_DATE']:
        executed_sql_str = exec_sql_str 
    else:
        executed_sql_str = g_date_sql_str + ORDER_BY_CRIT + sort_ord 
        
        
    #executed_sql_str =  exec_sql_str  if (tabtype != tabMap['tab_DATE']) else g_date_sql_str + ORDER_BY_CRIT + sort_ord 
#    executed_sql_str_2 =  exec_sql_str_page if (tabtype != tabMap['tab_DATE']) else g_date_sql_str 
 #   executed_sql_str =  exec_sql_str + ORDER_BY_CRIT + sort_ord
##########
# Start of Execution of SQL
#########
    #tabMap = {y:x for x,y in tabMap.iteritems()}
    tabMap = {y:x for x,y in tabMap.items()}

    print ("SORTER " + str(ORDER_BY_CRIT))
    print ("Exec webMark SQL " + executed_sql_str)
    print (str(tabtype) + " tab in play")

    conn = conn.connect()
    conn.text_factory = lambda x: x.decode("utf-8", errors = 'ignore')

    try:
        curs = conn.cursor()

        print(executed_sql_str)
        curs.execute(executed_sql_str, (user_id,))
        dbRows = curs.fetchall()

        rowCount = len(dbRows)
        print ("RowCountWB " + str(rowCount))
        print ("RowCountWBCursor " + str(curs.rowcount))
        
        print ("arg " + sessionID)
        sessObj = util.getSessionObject(sessionID)

        sessObj.DATASTORE = dbRows
        sessObj.ROWCOUNT = rowCount
        sessObj.ORDERBYCRIT = ORDER_BY_CRIT
        sessObj.SORT_ORD = sort_ord
        sessObj.USERID = user_id

        util.storeSessionObject(sessObj)
        
        conn.close()

    except Exception as inst:    
        print (inst)
        marks = Marks(tabMap[tabtype],None,None,Error(2000))
        #return marks.renderMainView(user_name,sort_crit,tabMap)
        
        return marks.renderMainView(user_id,sort_crit,tabMap)
    
    #return exec_page_nav(req,1,sessionID,tabtype)
    return exec_page_nav(1,sessionID,tabtype,init)


    
def exec_page_nav(page,sessionID,tabtype,init):
    tabMap = g.tabMap
    tabMap = {y:x for x,y in tabMap.items()}
    #rowsPerPage = util.unWrap(req,rowsPerPage)
    #rowsPerPage = 30
    rowsPerPage = 30


    
  
    page = int(page)

    data = ()
    i = 0
    j = 0

    sessObj = util.getSessionObject(sessionID)
    
    dataRows = sessObj.DATASTORE
    ORDER_BY_CRIT = sessObj.ORDERBYCRIT
    SORT_ORD = sessObj.SORT_ORD 
    rowCount = sessObj.ROWCOUNT
    totRows = rowCount
    
    user_id = sessObj.USERID

    #No results do not bother with rest below
    if rowCount == 0:
        dbRows=None
        sort_crit = ()
        return Marks(tabMap[tabtype],dbRows,rowCount).renderMainView(user_id,sort_crit,tabMap,page)

    print(dataRows[0][0])
    
#### REVISIT BELOW ##############
    if page > 1:
 
        page = page - 1
        i = page * rowsPerPage
        page = page + 1
        j = page * rowsPerPage
 
        if j > totRows:
            j = totRows
    else:
        i = 0
        if totRows > rowsPerPage:     #all logic to account for page 1 ( really a spec case here ) being first of potentially 
            j = rowsPerPage           #large result set or set less than a page
        elif totRows < rowsPerPage:
            j = totRows
            
        ##### python vs perl ######
        
#### REVISIT ABOVE ####
   
    sql_str = "  " + str(dataRows[i][0]) + "  "
   
    i = i + 1
    
    for qq in range(i,j):
        data =  dataRows[qq][0]
        sql_str += ", " + str(data) + "  " 
     
    sql_str +=  ") " + ORDER_BY_CRIT + " "
    sql_str += SORT_ORD

    executed_sql_str_page = main_sql_str_page + sql_str

    print(executed_sql_str_page)
#### SQL execute start
#######################
    conn = db.db_factory()
    conn = conn.connect()
    conn.text_factory = lambda x: x.decode("utf-8", errors = 'ignore')
    
    try:
        curs = conn.cursor()

        #curs.execute(executed_sql_str_page, (user_id,))
        curs.execute(executed_sql_str_page)
        dbRows = curs.fetchall()

    except Exception as inst:    
        print (inst)
        marks = Marks(tabMap[tabtype],None,None,Error(2000))
        #return marks.renderMainView(user_name,sort_crit,tabMap)
        return marks.renderMainView(user_id,sort_crit,tabMap)
###################
### sql execute end
    
    sort_crit = ()

    markObj = Marks(tabMap[tabtype],dbRows,rowCount)
    #return markObj.renderMainView(user_name,sort_crit,tabMap)

    if init:
        print ("First View")
        return markObj.renderMainView(user_id,sort_crit,tabMap,page)
    else:
        print("Other View")
        return markObj.renderTabTableView(user_id,sort_crit,tabMap,page)

#    return markObj.renderMainView(user_id,sort_crit,tabMap,page)
 
