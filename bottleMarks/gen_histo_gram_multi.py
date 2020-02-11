hist_sql_all_str = "select b.url, a.title, a.dateAdded from WM_BOOKMARK a, WM_PLACE b where a.PLACE_ID = b.PLACE_ID "

def gen_histogram():
    markHist = {}
    elimdups = {}
    histo_list = []
    (title,url,dateAdded) = (1,0,2)

    conn = sqlite3.connect(connFile)
    #conn.text_factory = bytes
    conn.text_factory = lambda x: x.decode("latin1")
    try:
        curs = conn.cursor()
        curs.execute(hist_sql_all_str, (user_id,))
        dbRows = curs.fetchall()
        print "RowCountWB " + str(len(dbRows))
        conn.close()
    except:
        pass

    for data in data_refs:
        if not data[title]:
            continue       
        if re.match(r'^\s*$',data[title]):
            continue
        if  title in elimdups:
            elimdups[title][url] = data[url]
            elimdups[data][title][dateAdded] = data[dateAdded]
        else:
            elimdups[data][title]] = [ url => [url], 
            dateAdded => data[dateAdded] 

        for kk in elimdups.keyitems:
            words = re.split('?:\s+, kk')

        for word in words:
            if  re.match(r'/(?:(\ba\b)|(\bfrom\b)|(\byour\b)|(\bHow\b)|(\bBE\b)|(\bas\b)|(\bthe\b)|(\bby\b)|(\bon\b)|(\band\b)|(\bis\b)|(\bFor\b)|(\bwith\b)|(\bIn\b)|(\bto\b)|(\bof\b)|(\b(\s+)\b)|(-|\+)|(\|)|[&-:><-#]',word):

            if re.match(r'/\b[[:cntrl:]]+\b/',word):
                continue     
            if not re.match(/[\x00-\x7f]/,word):
                continue 
            word = re.sub(r'\s+$',r'',word)
            word = re.sub(r'^\s+',r'',word)

            if word in markHist:
                markHist[word][count+=1]
            else:
                markHist[word] =  count = 1 


    #markHistHiLo = 
    #sort { b->[1] <=> $a->[1] } 
    #map ( [ $_, markHist[i][count] ])

    markHistHiLo =
    sorted(
       map( lambda x: [x, markHist[x][count] ]), markHist.keys())

    #new_list = sorted(old_list, key=f, cmp=lambda a,b:cmp(a[0],b[0]) or cmp(b[1],a[1]))
'''
    AT = 'A' 
    nxt = 3
    AL = ''
    FL = 0
    H = ()

    for mrow in markHistHiLo:
        if mrow[1] in H and FL == nxt:
            AL = AT 
            AT++
            H[mrow[1] + AL] = mrow[0];
            FL = 0
        elif ( mrow[1] + AL in H ):
            H[mrow[1] + AL] .= "|" . row[0]
            FL++
       else:
            H[mrow[1]] =  mrow[0]
            AL = ''
            FL = 0

##############################  
    H.sort(reverse=True) 
    HH.append(H[1]) 

    for my $k (sort { $b <=> $a}  keys %H) {
       push @H, $H{$k}
     
##############################
'''
def gen_optionListDiv():
    gen_histogram()
    str0 += '''#\n\t<option value=" "> </option>''';
    str1 += '''\n\t<option value=" "> </option>''';
    str2 += '''\n\t<option value=" "> </option>''';

    for option in HH[0:15]:
        option = re.sub(r'\|', r' ', option) 
        str0 += '''\n\t<option value=''' + option + '''> ''' + option + '''</option>''';

    for option in HH[15:30]:
        option = re.sub(r'\|', r' ', option) 
        str1 += '''\n\t<option value=''' + option + '''> ''' + option + '''</option>''';

    for option in HH[30:45]:
        option = re.sub(r'\|', r' ', option) 
        str2 += '''\n\t<option value=''' + option + '''> ''' + option + '''</option>''';

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

       </form>
       </div>
'''
    return out_hist_opts 


