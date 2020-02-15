hist_sql_all_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID "
import re
import sqlite3
import globals as g

# elim2 = { "greenich" : { "url" : 'ht://loop', 'dateAdded': '2001-12-02' }, "santan" : { "url": 'ht://loas', 'dateAdded': '2001-12-03'} }  
def gen_histogram():
    markHist = {}
    elimdups = {}
    histo_list = []
    (title,url,dateAdded) = (1,0,2)

    conn = sqlite3.connect(g.connFile)
    conn.text_factory = bytes
    #conn.text_factory = lambda x: x.decode("latin1")
    try:
        curs = conn.cursor()
        curs.execute(hist_sql_all_str)
        dbRows = curs.fetchall()
        print "RowCountWB " + str(len(dbRows))
        conn.close()
    except:
       print "Exception" 

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

    for title_str,v in elimdups.iteritems():
        words = re.split('\s+', title_str)

        for word in words:
            if re.match(r'\b[:cntrl:]+\b',word):
                continue
            if re.match(r"(?:[-+|:']|\bsqft\b|\bof\b|\bThe\b|\bthe\b|\bto\b|\band\b|\b[0-9]\b)",word,re.I):
                continue
            if re.match(r"'",word):
                continue
            if not re.match(r'[\x00-\x7f]',word):
                continue 
            word = re.sub(r'\s+$','',word)
            word = re.sub(r'^\s+','',word)

            if word in markHist:
                markHist[word]['count'] += 1
            else:
                markHist[word] =  { 'count' : 1 }

    new_list = sorted( map(lambda x: [x, markHist[x]['count']],markHist.keys()),  key=lambda hist : hist[1] , reverse=True)


    #markHistHiLo = sorted( map(lambda x: [x, markHist[x]['count']],markHist.keys()), reverse=True)
    #new_list = sorted(old_list, key=f, cmp=lambda a,b:cmp(a[0],b[0]) or cmp(b[1],a[1]))
    #pretty =  new_list[1][1] < 100  and  "*" * (new_list[1][1]/100)  or  "#" * new_list[1][1]
    for line in new_list:
        pretty =  line[1] > 100  and  "*" * (line[1]/100)  or  "#" * line[1]
        print line[0] + "\t\t\t\t" + pretty + " " + str(line[1])
gen_histogram()
