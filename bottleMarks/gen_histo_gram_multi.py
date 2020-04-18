#hist_sql_all_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID "
hist_sql_all_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID and a.USER_ID = ? "
import re
import sqlite3
import globals as g

# elim2 = { "greenich" : { "url" : 'ht://loop', 'dateAdded': '2001-12-02' }, "santan" : { "url": 'ht://loas', 'dateAdded': '2001-12-03'} }  

def gen_histogram(user_id):
    markHist = {}
    elimdups = {}
    histo_list = []
    (title,url,dateAdded) = (1,0,2)

    conn = sqlite3.connect(g.connFile)
    #conn.text_factory = bytes
    conn.text_factory = lambda x: x.decode("latin1")
    try:
        curs = conn.cursor()
        curs.execute(hist_sql_all_str,(user_id,))
        dbRows = curs.fetchall()
        print "RowCountWB " + str(len(dbRows))
        conn.close()
    except Exception as ex:
       print "Exception" + ex 
       raise ex
 
    for data in dbRows:
        if not data[title]:
            continue       
        if re.match(r'^\s*$',data[title]):
            continue
        if  data[title].upper() in elimdups:
            continue
        else:
            elimdups[data[title].upper()] = { "url": data[url], "dateAdded": data[dateAdded] }

    for title_str,v in elimdups.iteritems():
        words = re.split('\s+', title_str)

        for word in words:
            if re.match(r'\b[:cntrl:]+\b',word):
                continue
            if re.match(r"(?:[-+|:'&]|\bsqft\b|\bof\b|\bWith\b|\bThe\b|\bthe\b|\bto\b|\band\b|\b[0-9]\b)",word,re.I):
                continue
            if re.match(r"(?:\ba\b|\be\b)",word,re.I):
                continue
            if len(word) < 3 :
                continue
            if not re.match(r'[\x00-\x7f]',word):
                continue 
            word = re.sub(r'\s+$','',word)
            word = re.sub(r'^\s+','',word)

            if word in markHist:
                markHist[word]['count'] += 1
            else:
                markHist[word] =  { 'count' : 1 }

    #new_list = sorted( map(lambda x: [x, markHist[x]['count']],markHist.keys()),  key=lambda hist : hist[1] , reverse=True)
    HH = sorted( map(lambda x: [x, markHist[x]['count']],markHist.keys()),  key=lambda hist : hist[1] , reverse=True)
    return HH

def gen_optionListDiv(user_id):
    HH = gen_histogram(user_id)

    str0 = '''\n\t<option value=" "> </option>''';
    str1 = '''\n\t<option value=" "> </option>''';
    str2 = '''\n\t<option value=" "> </option>''';
    str3 = '''\n\t<option value=" "> </option>''';

    for option in HH[0:15]:
      #  option = re.sub(r'\|', r' ', option) 
        str0 += '''\n\t<option value=''' + option[0] + '''> ''' + option[0] + '''</option>''';

    for option in HH[15:30]:
      #  option = re.sub(r'\|', r' ', option) 
        str1 += '''\n\t<option value=''' + option[0] + '''> ''' + option[0] + '''</option>''';

    for option in HH[30:45]:
      #  option = re.sub(r'\|', r' ', option) 
        str2 += '''\n\t<option value=''' + option[0] + '''> ''' + option[0] + '''</option>''';

    for option in HH[45:60]:
      #  option = re.sub(r'\|', r' ', option) 
        str3 += '''\n\t<option value=''' + option[0] + '''> ''' + option[0] + '''</option>''';

    out_hist_opts = '''
       <div style="display:inline-block" id="optionDiv">
       <form>
      <select  onchange="topOpToSearch(this.options[this.options.selectedIndex].text);" id="topOptionID" name="topOption">
  <!--       <select  onblur="topOpToSearch(this.options[this.options.selectedIndex].text);" id="topOptionID" name="topOption"> -->
        ''' +   str0 + ''' 
       </select>
      <select  onchange="topOpToSearch(this.options[this.options.selectedIndex].text);" id="topOptionID" name="topOption">
          ''' +  str1  + '''
       </select>
      <select  onchange="topOpToSearch(this.options[this.options.selectedIndex].text);" id="topOptionID" name="topOption">
         ''' + str2 + ''' 
       </select>

      <select  onchange="topOpToSearch(this.options[this.options.selectedIndex].text);" id="topOptionID" name="topOption">
         ''' + str3 + ''' 
       </select>

       </form>
       </div>
'''
    return out_hist_opts 


