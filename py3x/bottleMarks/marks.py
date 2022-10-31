from bottle import template
import datetime
import time
import gen_histo_gram_multi as hist
import re
import html

class Marks(object):

    def __init__(self,tab=None, dbObject=None,rowCount=None, errObj=None):
        self.tab = tab
        self.dbObject = dbObject
        self.rowCount = rowCount
        self.errObj = errObj

    def renderMainView(self,user_id,sort_crit,tabMap,page=None):

        tabTable = self.genTabTable(sort_crit,self.tab)        
        pageLinkNavs = self.genNavigation(page)
        print("LOOK")
        optionTops=hist.gen_optionListDiv(user_id)
        return template('class_mainview', user_id=user_id, sort_crit=sort_crit,
               tabMap=tabMap, tab=self.tab, tabTable=tabTable, pageLinkNavs=pageLinkNavs,optionTops=optionTops)


    def renderDefaultView(self,colorStyle="red",displayText=str()):
        colorStyle="red"
        tab = 6
        user_name = "aab"
        return template('class_defaultpage', displayText=displayText, colorStyle=colorStyle,
                                     tab=tab, user_name=user_name)

    def renderRegistrationView(self,errText=None):
        if not errText:
            errText = ""
        return template('class_registration.html', errText=errText)
   
    def renderErrorPageView(self):
        return template('class_not_found.html')

    def renderErrorPageView2(self,errText=None):
        if not errText:
            errText = ""
        return template('class_not_found.html', errText=errText)

    def renderTabTableView(self,user_id,sort_crit,tabMap,page):
        tabTable = self.genTabTable(sort_crit,self.tab)        
        optionTops=hist.gen_optionListDiv(user_id)
        print ("redder")
        return template('class_tab_view', user_id=user_id, sort_crit=sort_crit, tabMap=tabMap, tab=self.tab, tabTable=tabTable, optionTops=optionTops)  
 
    def genNavigation(self, page):

        rowsPerPage = 30
        pgCnt = 1
        currCnt = 0
        buffer_out = ()
        
        totRows = self.rowCount
        print ("total rows " + str(totRows))
        #rowsPerPage = self.ROWSPERPAGE
        
        if totRows > rowsPerPage:
            buffer_out = "<div>"
            buffer_out +=  "Pages: "   
            while currCnt < totRows:                 
                if page == pgCnt:
                    buffer_out += " <span style='font-weight:bolder' id='curr_page'> " +  str(pgCnt) + " </span>"
                else:
                    buffer_out += "<span> <A HREF=javascript:jax_cgi_out(" + str(pgCnt) + ")>" + str(pgCnt) +  "</A> </span>"

                currCnt += rowsPerPage
                pgCnt += 1            
            buffer_out += "</div>"
            print ("currCnt " + str(currCnt))
        return buffer_out 

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


    def genTabTable(self,sort_crit,tab):

        sort_span_html_asc = "<span id='sort_span_date'>  &uarr; </span>"
        sort_span_html_dsc = "<span id='sort_span_date'>  &darr; </span>"

        if sort_crit == 2:
            sort_sp_dt = sort_span_html_asc
        elif sort_crit == 3:
            sort_sp_dt = sort_span_html_dsc
        else:
            sort_sp_dt = " "
  
        
        tbl = '''<table  id='tab_table' class='tab_table'>
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
  
            tbl_row  += "<tr class=" + row_color + "> "  + tbl_row_header + "<td class='title_cell'> <a href=" + str(url) + " target='_blank'> "  +  str(title) + " </a> </td>" \
            + " <td class='url_cell'> " +  str(url) + " </td> " \
            + "<td class='date_cell'> "  + str(added) + " </td>"  \
            + " </tr> \n "
            
            title = re.sub(r'"',r'\"',title)
            title = re.sub(r"'",r"`",title) #workaround for single quotes use apostrophe to soothe js

  

        if self.rowCount:
           tbl += tbl_row  + "<!-- Row Count" + str(self.rowCount) + " -->"  + "</table>\n"

        div_table = " <div id=\"div_tab_table\" > "
        div_table += tbl
        div_table += "</div>"

        return div_table


    def convertTime(self, dateAdded):
        dateAdded = datetime.datetime.fromtimestamp( dateAdded/(1000 * 1000) ).strftime("%m-%d-%Y %H:%M:%S")
        return dateAdded
