from flask import render_template
import gen_histo_gram_multi as hist
import time

class Marks(object):

    def __init__(self,tab=None, dbObject=None,rowCount=None, errObj=None):
        self.tab = tab
        self.dbObject = dbObject
        self.rowCount = rowCount
        self.errObj = errObj

    def renderMainView(self,user_id,sort_crit,tabMap):
        tabTable = self.genTabTable(sort_crit)        
        optionTops=hist.gen_optionListDiv(user_id)
        tabMap = {y:x for x,y in tabMap.items()}
        return render_template('class_mainview.html', user_id=user_id, sort_crit=sort_crit, tabMap=tabMap, tab=self.tab, tabTable=tabTable, optionTops=optionTops)


    def renderDefaultView(self,colorStyle="red",displayText=str()):
        colorStyle="red"
        tab = 6
        user_name = "aab"
        return render_template('class_defaultpage.html', displayText=displayText, colorStyle=colorStyle,
                                     tab=tab, user_name=user_name)

    def renderRegistrationView(self,errText=""):
        return render_template('class_registration.html', errText=errText)


    def genError(self):
        errObj = self.errObj
        errText = errObj.errText()
        errOut = '''
<div>
  <ul>
   <li style="font-size:16px; color:red"> ''' + errText + '''  </li>
  </ul>
</div>
'''
        return errOut


    def genTabTable(self,sort_crit):

        sort_span_html_asc = "<span id='sort_span_date'>  &uarr; </span>"
        sort_span_html_dsc = "<span id='sort_span_date'>  &darr; </span>"

        if sort_crit == 2:
            sort_sp_dt = sort_span_html_asc
        elif sort_crit == 3:
            sort_sp_dt = sort_span_html_dsc
        else:
            sort_sp_dt = " "
  

        tbl = '''<table id='tab_table' class='tab_table'>\n 
                 <col width='50%'>\n
                 <col width='35%'>\n
                 <col width='auto'>\n
                '''    

        tbl += " <tr class='header_row'><th>Title</th><th>LINK</th><th style='background:red' " + " onClick=\"cgi_out('tab=11')\"> Date Added " +  sort_sp_dt  + "  </th></tr>\n "

        ## POTENTIAL ERROR SECTION ##
        if self.errObj:
            tbl += self.genError()
  

        ## POTENTIAL ERROR SECTION ##
        if not self.dbObject:
            tbl += "<tr id=\"NoResults\"><td> No Results for Query </td></tr> \n </table>"
            return tbl

        i=0
        tbl_row = str()
        for row in self.dbObject:
            (url,title,added) = (row[0],row[1],row[2])
            bk_id = row[3]
            added = self.convertTime(added)
            i += 1
            alt =  (i % 2) or 2    
            row_color = "row_color" + str(alt)
            
            tbl_row_header = ' <th hidden> ' + str(bk_id) + ' </th> ';
                        
#            tbl_row  += "<tr class=" + row_color +"> " + "<td class='title_cell'> <a href=" + str(url) + " target='_blank'> "  +  str(title) + " </a> </td>" \
            tbl_row  += "<tr class=" + row_color + "> "  + tbl_row_header + "<td class='title_cell'> <a href=" + str(url) + " target='_blank'> "  +  str(title) + " </a> </td>" \
            + " <td class='url_cell'> " +  str(url) + " </td> " \
            + "<td class='date_cell'> "  + str(added) + " </td>" \
            + " </tr> \n "

        if self.rowCount:
           tbl += tbl_row  + "<!-- Row Count" + str(self.rowCount) + " -->"  + "</table>\n"

        return tbl

    def convertTime(self, dateAdded):
        (year, mon, day, hour, mins, secs)  = time.localtime( dateAdded/(1000 * 1000))[0:6]
        curr_date_tuple  = time.localtime( dateAdded/(1000 * 1000))
        day_of_week = time.strftime("%a",curr_date_tuple)
        dateAdded = ('{}-{}-{} {}:{}:{}').format(mon,day,year,hour,mins,secs)
        #dateAdded = ('{}-{}-{} {}:{}:{} {}').format(mon,day,year,hour,mins,secs, day_of_week)
        return dateAdded

    def convertDateEpoch(self, humanDate):
        res = re.match(r'([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})',humanDate)
        year = res.group(1) 
        month = res.group(2) 
        day = res.group(3)
        dateAdded = datetime.datetime(year,month,day,0,0).strftime('%s')
        dateAdded = dateAdded * (1000 * 1000);
        return dateAdded
        #datetime.datetime(2012,4,1,0,0).timestamp()
