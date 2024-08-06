hist_sql_all_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID "
import re
from connection_factory  import db_factory as db

def gen_histogram():
    markHist = {}
    elimdups = {}
    histo_list = []
    (title,url,dateAdded) = (1,0,2)

    conn = db().connect()
    conn.text_factory = lambda x: x.decode("utf-8", errors='ignore')

    try:
        curs = conn.cursor()
        curs.execute(hist_sql_all_str)
        dbRows = curs.fetchall()
        print ("RowCountWB " + str(len(dbRows)))
        conn.close()

    except Exception as ex:
       print (str(ex)) 
       raise ex

    for data in dbRows:
        if not data[title]:
            continue       
        if re.match(r'^\s*$',data[title]):
            continue
        if  data[title].upper() in elimdups:
            continue
            elimdups[title][url] = data[url]
            elimdups[data][title][dateAdded] = data[dateAdded]
        else:
            elimdups[data[title].upper()] = { "url": data[url], "dateAdded": data[dateAdded] }

    for title_str,v in elimdups.items():
        words = re.split(r'\s+', title_str)

        for word in words:
            if re.match(r'\b[:cntrl:]+\b',word):
                continue
            if re.match(r"(?:[-+|:']|\bsqft\b|\bof\b|\bThe\b|\bthe\b|\bto\b|\band\b|\b[0-9]\b)",word,re.I):
                continue
            if re.match(r"(?:[-+|:']|\bbd\b|\bba\b|\bfor\b)",word,re.I):
                continue
            if re.match(r"'",word):
                continue
            if not re.match(r'[\x00-\x7f]',word):
                continue 
            if len(word) < 3:
                continue 

            word = re.sub(r'\s+$','',word)
            word = re.sub(r'^\s+','',word)

            if word in markHist:
                markHist[word]['count'] += 1
            else:
                markHist[word] =  { 'count' : 1 }

    count=1
    new_list = sorted( map( lambda word: [ word, markHist[ word ] ['count'] ]       #1 -- map ( function/lambda,  
                            , markHist.keys())                                      # iterable ) 
                            , key=lambda birdie : birdie[count]                     #2 -- key to sort       **args to sorted()** 
                            , reverse=True)                                         #3 -- reverse order ?

                            # the option "key" --> takes a func/lambda that transforms the list to be
                            # sorted -- in this case what comes from the map -- and uses that instead 
                            # to sort the list -> count in this case 


    for line in new_list:

        pretty =            ( line[1] >=   100  and                    "*" * int(line[1]/100) )
        pretty = pretty or  ( line[1] <=  100   and line[1] > 10 and    "#" * int(line[1]/10)  )
        pretty = pretty or  ( line[1] <=  10    and line[1] > 5  and    "-" * int(line[1])     )
        pretty = pretty or  ( line[1] <=  5     and                     "!" * int(line[1])     )

        print ('%-35s%5d %-50s' % 
                                    (line[0].encode('utf-8', errors='replace').decode('ascii', errors='ignore'),
                                                        line[1],
                                                                                pretty))

def agg(w_list):

    for  line in w_list:
        if line[1]  == last_line:
            liner  = liner + "|" + line[0]
        else:
           last_line = line[1]


gen_histogram()
