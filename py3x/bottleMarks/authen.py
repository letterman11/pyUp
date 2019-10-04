from functools import wraps


### decorator functions
def authenticate(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		#(user_id,user_name)= pre_auth(gConn)
		if not pre_auth(connFile) or  not validate_session():
			return Marks().renderDefaultView()
		return f(*args, **kwargs)
	return wrapper


def pre_auth(connFile):
	usr_name = "" 
	usr_pass = ""
	old_usr_pass = ""
	try:
		usr_name = request.params['user_name'] 
		usr_pass = request.params['user_pass'] 
		old_usr_pass = request.params['old_user_pass']  
	except:
		pass		
	exec_sql_str = str()

	if old_usr_pass:
		exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" + old_usr_pass +  "' and user_name ='"  + usr_name + "' "
	else:
		exec_sql_str = "select user_id, user_name from WM_USER where user_passwd = '" + usr_pass + "' and user_name ='" + usr_name  + "' "

	### error checking ????? ##############
	conn = sqlite3.connect(webMarkDbFile)
	curs = conn.cursor()
	curs.execute(exec_sql_str)
	user_row = curs.fetchall()
	conn.close()

	print usr_name
	print usr_pass + "User PASS"
	return user_row
