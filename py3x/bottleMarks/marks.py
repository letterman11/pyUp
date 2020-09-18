from bottle import template
import datetime
import gen_histo_gram_multi as hist
import re
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
        return template('class_mainview', user_id=user_id, sort_crit=sort_crit, tabMap=tabMap, tab=self.tab, tabTable=tabTable, optionTops=optionTops)


    def renderDefaultView(self,colorStyle="red",displayText=str()):
        colorStyle="red"
        tab = 6
        user_name = "aab"
        return template('class_defaultpage', displayText=displayText, colorStyle=colorStyle,
                                     tab=tab, user_name=user_name)

    def renderRegistrationView(self):
        errText = ""
        return template('class_registration.html', errText=errText)




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
  

        tbl = '''<table class='tab_table'>\n 
                 <col width='50%'>\n
                 <col width='35%'>\n
                 <col width='auto'>\n
                '''    

        tbl += " <tr class='header_row'><th>Title</th><th>LINK</th><th style='background:red' " + " onClick='cgi_out('tab=11')> Date Added " +  sort_sp_dt  + "  </th></tr>\n "

        ## POTENTIAL ERROR SECTION ##
        if self.errObj:
            tbl += self.genError()
  

        ## POTENTIAL ERROR SECTION ##
        if not self.dbObject:
            return tbl

        i=0
        tbl_row = str()
        for row in self.dbObject:
            (url,title,added) = (row[0],row[1],row[2])
            added = self.convertTime(added)
            i += 1
            alt =  (i % 2) or 2    
            row_color = "row_color" + str(alt)
            tbl_row  += "<tr class=" + row_color +"> " + "<td class='title_cell'> <a href=" + url + " target='_blank'> "  +  title + " </a> </td>" \
            + " <td class='url_cell'> " +  url + " </td> " \
            + "<td class='date_cell'> "  + str(added) + " </td>" \
            + " </tr> \n "

        if self.rowCount:
           tbl += tbl_row  + "<!-- Row Count" + str(self.rowCount) + " -->"  + "</table>\n"

        return tbl

    def convertTime(self, dateAdded):
#        dateAdded = datetime.datetime.fromtimestamp( dateAdded/(1000 * 1000) ).strftime("%m-%d-%Y %H:%M:%S")
        (year, mon, day, hour, mins, secs)  = time.localtime( dateAdded/(1000 * 1000))[0:6]
        dateAdded = ('{}-{}-{} {}:{}:{}').format(mon,day,year,hour,mins,secs)

        return dateAdded
