from bottle import template

class Marks:

	def __init__(self,tab=1, dbObject=1,rowCount=1, errObj=1):
		self.tab = tab
		self.dbObject = dbObject
		self.rowCount = rowCount
		self.errObj = errObj

	def renderMainView(self,user_id,sort_crit,tabMap):
		
		return template('class_mainview', user_id=user_id, sort_crit=sort_crit, tabMap=tabMap, tab=self.tab)


	def renderDefaultView(self):
		colorStyle="red"	
		displayText =  ""
		tab = 6
		user_name = "aab" 
		return template('class_defaultpage', displayText=displayText, colorStyle=colorStyle, 
										tab=tab, user_name=user_name) 

	def renderRegistrationView(self):
		self.errText = ""
		return template('class_registration.html', errText=self.errText) 


	def genTabTable(self):

		sort_span_html_asc = "<span id=\"sort_span_date\">  &uarr; </span>"
		sort_span_html_dsc = "<span id=\"sort_span_date\">  &darr; </span>"

		if sort_crit == 2:
			sort_sp_dt = sort_span_html_asc
		elif sort_crit == 3:
			sort_sp_dt = sort_span_html_dsc
		else:
			sort_sp_dt = " "
  

		tbl = ''' <table class='tab_table'>\n 
				 <col width="50%">\n
				 <col width="35%">\n
				 <col width="auto">\n
				'''
		tbl += " <tr class='header_row'><th>Title</th><th>LINK</th><th style=background:red' "
		+ " onClick='cgi_out('tab=11');'> Date Added " +  sort_sp_dt + "  </th></tr>\n "

		## POTENTIAL ERROR SECTION ##
		if self.ERROROBJ:
			tbl += self.genError();
  

		## POTENTIAL ERROR SECTION ##
		for row in self.dbObject:
			(url,title,added) = (row[0],row[1],row[2])
			added = convertTime(added)
			i+=1
			alt =  i % 2 or 1    
			row_color = "row_color" + alt
			tbl_row  += "<tr class=" + row_color +"> "
			+ "<td class='title_cell'> <a href=" + url + " target='_blank'> "  +  title + " </a> </td>"
			+ " <td class='url_cell'> " +  url + " </td> "
			+ "<td class='date_cell'> "  + added + " </td>"
			+ " </tr> \n "

			if tbl_row:
				tbl += tbl_row 
			tbl += "</table>\n"

		return tbl


