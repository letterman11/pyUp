"""
BottleMarks experimental 
author: angus brooks -- refactored and cleaned via ai
"""
from bottle import Bottle, request, response, static_file, error as bottle_error
from datetime import datetime
from functools import wraps
import time
import re
import logging

from marks import Marks
from PJJExecPageSQL import exec_page, exec_page_nav
import lib.util_db as util
import connection_factory as db
from error import Error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Bottle()

# Configuration
APP_COOKIE_PATH = "/ex2WebMarks"
FIVE_DAY_SECONDS = 60 * 60 * 24 * 5
MIN_PASSWORD_LENGTH = 6
EMAIL_REGEX = r"^[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+"
DEFAULT_ROWS_PER_PAGE = 30
DEFAULT_TAB_ROWS_PER_PAGE = 15
DEFAULT_TAB = 9
DEFAULT_SORT_CRIT = 3


# Database helper functions
def get_db_connection():
    """Create and return a database connection."""
    return db.db_factory().connect()


def get_placeholder():
    """Get the database-specific placeholder."""
    return db.db_factory.place


# Static file routes
STATIC_ROUTES = [
    ('/public/css/<filename>', '/static/css/<filename>', '/static/ex2/css/<filename>', './public/css'),
    ('/public/images/<filename>', '/static/images/<filename>', None, './public/images'),
    ('/public/js/<filename>', '/static/js/<filename>', '/static/ex2/js/<filename>', './public/js'),
]


def create_static_route(routes, root_dir):
    """Create static file serving routes."""
    @app.route(routes[0])
    @app.route(routes[1])
    def serve_static(filename):
        return static_file(filename, root=root_dir)
    
    if routes[2]:
        @app.route(routes[2])
        def serve_static_alt(filename):
            return static_file(filename, root=root_dir)


for routes, root in [(r[:3], r[3]) for r in STATIC_ROUTES]:
    create_static_route(routes, root)


# Authentication decorator
def authenticate(f):
    """Decorator to ensure user is authenticated."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not validate_session(request):
            return Marks().renderDefaultView()
        return f(*args, **kwargs)
    return wrapper


def validate_session(req):
    """Validate user session from request."""
    return util.validateSessionDB(req)


def set_auth_cookies(user_id, user_name, session_id):
    """Set authentication cookies for user session."""
    expire_time = int(time.time()) + FIVE_DAY_SECONDS
    
    cookies = {
        'wmSessionID': session_id,
        'wmUserID': user_id,
        'wmUserName': user_name,
        'Counter': '0'
    }
    
    for name, value in cookies.items():
        response.set_cookie(name, str(value), path=APP_COOKIE_PATH, expires=expire_time)
    
    util.saveSessionDB(session_id, user_id)
    logger.info(f"User {user_id} authenticated successfully")
    
    return session_id


# User authentication class
class UserAuth:
    """Handle user authentication operations."""
    
    @staticmethod
    def authenticate_user(username, password, old_password=None):
        """
        Authenticate user with username and password.
        Returns (user_id, username, password) tuple or None.
        """
        if not username or not password:
            return None
        
        password_hash = util.digest_pass(password)
        old_password_hash = util.digest_pass(old_password) if old_password else None
        
        place = get_placeholder()
        query = f"SELECT user_id, user_name, user_passwd FROM WM_USER WHERE user_name = {place}"
        
        conn = None
        try:
            conn = get_db_connection()
            curs = conn.cursor()
            curs.execute(query, (username,))
            db_row = curs.fetchone()
            
            if not db_row:
                return None
            
            db_user_id, db_username, db_password = db_row
            
            # Check for password update scenario
            if old_password and (db_password == old_password or db_password == old_password_hash):
                return (db_user_id, db_username, password)
            
            # Check normal authentication
            if db_password == password or db_password == password_hash:
                return (db_user_id, db_username, db_password)
            
            return None
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def register_user(username, password, email):
        """
        Register a new user.
        Returns True on success, raises exception on failure.
        """
        # Generate user ID
        part_id = util.genSessionID()[:5]
        user_id = f"{username[:5]}_{part_id}"
        
        # Hash password
        password_hash = util.digest_pass(password)
        
        place = get_placeholder()
        query = f"INSERT INTO WM_USER (USER_ID, USER_NAME, USER_PASSWD, EMAIL_ADDRESS) VALUES ({place}, {place}, {place}, {place})"
        
        conn = None
        try:
            conn = get_db_connection()
            curs = conn.cursor()
            curs.execute(query, (user_id, username, password_hash, email))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_password(username, new_password):
        """Update user password."""
        password_hash = util.digest_pass(new_password)
        place = get_placeholder()
        query = f"UPDATE WM_USER SET USER_PASSWD = {place} WHERE USER_NAME = {place}"
        
        conn = None
        try:
            conn = get_db_connection()
            curs = conn.cursor()
            curs.execute(query, (password_hash, username))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Password update error: {e}")
            return False
        finally:
            if conn:
                conn.close()


# Bookmark operations class
class BookmarkManager:
    """Handle bookmark CRUD operations."""
    
    @staticmethod
    def check_duplicate(user_id, url):
        """Check if bookmark URL already exists for user."""
        place = get_placeholder()
        query = f"""
            SELECT b.url FROM WM_BOOKMARK a, WM_PLACE b 
            WHERE a.PLACE_ID = b.PLACE_ID 
            AND a.USER_ID = {place} 
            AND b.URL = {place}
        """
        
        conn = None
        try:
            conn = get_db_connection()
            curs = conn.cursor()
            curs.execute(query, (user_id, url))
            result = curs.fetchone() is not None
            return result
        except Exception as e:
            logger.error(f"Duplicate check error: {e}")
            return False
        finally:
            if conn:
                conn.close()


    @staticmethod
    def insert_bookmark(user_id, title, url):
        """Insert new bookmark for user."""
        #bookmark_id, place_id = BookmarkManager.get_next_ids()
        
        unix_time = int(time.time())
        timestamp = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
        
        place = get_placeholder()
        place_query = f"INSERT INTO WM_PLACE (URL, TITLE) VALUES ({place}, {place})"
        bookmark_query = f"""
            INSERT INTO WM_BOOKMARK (USER_ID, PLACE_ID, TITLE, DATEADDED, DATE_ADDED) 
            VALUES ({place}, {place}, {place}, {place}, {place})
        """
        
        conn = None
        try:
            conn = get_db_connection()
            conn.autocommit = False
            curs = conn.cursor()
            
            curs.execute(place_query, (url, title))

            place_id = curs.lastrowid

            curs.execute(bookmark_query, (user_id, place_id, title, unix_time, timestamp))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Insert bookmark error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_bookmark(bookmark_id, title, url):
        """Update existing bookmark."""
        place = get_placeholder()
        
        conn = None
        try:
            conn = get_db_connection()
            conn.autocommit = False
            curs = conn.cursor()
            
            # Get place_id
            select_query = f"SELECT PLACE_ID FROM WM_BOOKMARK WHERE BOOKMARK_ID = {place}"
            curs.execute(select_query, (bookmark_id,))
            place_id = curs.fetchone()[0]
            
            # Update both tables
            update_bookmark_query = f"UPDATE WM_BOOKMARK SET TITLE = {place} WHERE BOOKMARK_ID = {place}"
            update_place_query = f"UPDATE WM_PLACE SET URL = {place}, TITLE = {place} WHERE PLACE_ID = {place}"
            
            curs.execute(update_bookmark_query, (title, bookmark_id))
            curs.execute(update_place_query, (url, title, place_id))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Update bookmark error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete_bookmark(bookmark_id):
        """Delete bookmark."""
        place = get_placeholder()
        
        conn = None
        try:
            conn = get_db_connection()
            conn.autocommit = False
            curs = conn.cursor()
            
            # Get place_id
            select_query = f"SELECT PLACE_ID FROM WM_BOOKMARK WHERE BOOKMARK_ID = {place}"
            curs.execute(select_query, (bookmark_id,))
            place_id = curs.fetchone()[0]
            
            # Delete from both tables
            delete_place_query = f"DELETE FROM WM_PLACE WHERE PLACE_ID = {place}"
            delete_bookmark_query = f"DELETE FROM WM_BOOKMARK WHERE BOOKMARK_ID = {place}"
            
            curs.execute(delete_place_query, (place_id,))
            curs.execute(delete_bookmark_query, (bookmark_id,))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Delete bookmark error: {e}")
            raise
        finally:
            if conn:
                conn.close()


# View rendering helper functions
def get_user_from_request():
    """Extract user_id and user_name from request."""
    user_id = request.params.get('user_name') or request.get_cookie('wmUserID')
    user_name = request.params.get('user_name') or request.get_cookie('wmUserName')
    return user_id, user_name


def get_rows_per_page(default=DEFAULT_ROWS_PER_PAGE):
    """Extract rows per page from request parameters."""
    try:
        return int(request.params['rowsPerPage'])
    except (KeyError, ValueError):
        return default


def get_session_id():
    """Get session ID from cookies."""
    return request.get_cookie('wmSessionID')


def render_main_view(user_id=None, err_obj=None, session_id=None, init=True):
    """Render main application view."""
    if not user_id:
        user_id, user_name = get_user_from_request()
    else:
        user_name = request.get_cookie('wmUserName')
    
    rows_per_page = get_rows_per_page(DEFAULT_ROWS_PER_PAGE)
    
    if not session_id:
        session_id = get_session_id()
    
    return exec_page(request, user_id, user_name, err_obj, session_id, rows_per_page, init)


def render_tab_table_view(tab, init=False, user_id=None, err_obj=None):
    """Render tab table view."""
    if not user_id:
        user_id, user_name = get_user_from_request()
    else:
        user_name = request.get_cookie('wmUserName')
    
    session_id = get_session_id()
    rows_per_page = get_rows_per_page(DEFAULT_TAB_ROWS_PER_PAGE)
    
    return exec_page(request, user_id, user_name, err_obj, session_id, rows_per_page, init)


def render_tab_table_view_nav(page, rows_per_page, init=False, user_id=None, err_obj=None):
    """Render tab table view with navigation."""
    if not user_id:
        user_id, user_name = get_user_from_request()
    else:
        user_name = request.get_cookie('wmUserName')
    
    try:
        sort_crit = int(request.params['sortCrit'])
    except (KeyError, ValueError):
        sort_crit = DEFAULT_SORT_CRIT
    
    session_id = get_session_id()
    
    try:
        tab = int(request.get_cookie('tab'))
    except (TypeError, ValueError):
        tab = DEFAULT_TAB
    
    return exec_page_nav(page, session_id, tab, sort_crit, rows_per_page, False)


# Public routes
@app.route("/ex2WebMarks/registration")
@app.route('/registration')
def register_page():
    """Display registration page."""
    return Marks().renderRegistrationView()


@app.post("/ex2WebMarks/regAuth")
@app.post('/regAuth')
def register_auth():
    """Handle user registration."""
    try:
        username = request.params['user_name']
        password1 = request.params['new_user_pass1']
        password2 = request.params['new_user_pass2']
        email = request.params['email_address']
    except KeyError:
        return Marks().renderRegistrationView(Error(112).errText())
    
    # Validation
    if not username or not password1 or not password2:
        return Marks().renderRegistrationView(Error(107).errText())
    
    if password1 != password2:
        return Marks().renderRegistrationView(Error(113).errText())
    
    if len(password1) < MIN_PASSWORD_LENGTH:
        return Marks().renderRegistrationView(Error(111).errText())
    
    if not re.match(EMAIL_REGEX, email):
        return Marks().renderRegistrationView(Error(119).errText())
    
    # Register user
    try:
        UserAuth.register_user(username, password1, email)
        return Marks().renderDefaultView("red", f"Successfully Registered {username}")
    except Exception:
        return Marks().renderRegistrationView(Error(120).errText())


@app.route("/ex2WebMarks/default")
@app.route('/default')
def log_in():
    """Display login page."""
    return Marks().renderDefaultView()


@app.post("/ex2WebMarks/authenCred")
@app.post("/authenCred")
def authen_cred():
    """Authenticate user credentials."""
    username = util.unWrap(request, 'user_name')
    password = util.unWrap(request, 'user_pass')
    old_password = util.unWrap(request, 'old_user_pass')
    
    auth_result = UserAuth.authenticate_user(username, password, old_password)
    
    if auth_result:
        user_id, user_name, user_pass = auth_result
        session_id = util.genSessionID()
        set_auth_cookies(user_id, user_name, session_id)
        return render_main_view(user_id, None, session_id)
    else:
        return Marks().renderDefaultView(colorStyle="red", displayText=Error(112).errText())


@app.route("/ex2WebMarks/logout")
@app.route("/logout")
def log_out():
    """Log out user."""
    return Marks().renderDefaultView()


# Protected routes
@app.route("/ex2WebMarks")
@app.route("/")
@authenticate
def index():
    """Main application page."""
    return render_main_view()


@app.route("/ex2WebMarks/webMarks")
@app.route("/webMarks")
@authenticate
def index_web_marks():
    """Web marks view."""
    return render_main_view()


@app.route("/ex2WebMarks/tabView")
@app.route("/tabView")
@authenticate
def index_tab_view():
    """Tab view."""
    return render_main_view()


@app.route("/ex2WebMarks/tabTableView")
@app.route("/tabTableView")
@authenticate
def tab_table_view():
    """Tab table view."""
    return render_tab_table_view(1)


#@app.route("/ex2WebMarks/tabTableViewNav/<page:int>/<rowsPerPage:int>")
@app.route("/ex2WebMarks/tabTableViewNav/<page:int>/<rows_per_page:int>")
#@app.route("/tabTableViewNav/<page:int>/<rowsPerPage:int>")
@app.route("/tabTableViewNav/<page:int>/<rows_per_page:int>")
@authenticate
def tab_table_view_nav(page, rows_per_page):
    """Tab table view with navigation."""
    return render_tab_table_view_nav(page, rows_per_page)


@app.post("/ex2WebMarks/searchMark")
@app.post("/searchMark")
@authenticate
def search_web_mark():
    """Search bookmarks."""
    return render_main_view(init=False)


@app.post("/ex2WebMarks/insertMark")
@app.post("/insertMark")
@authenticate
def add_web_mark():
    """Add new bookmark."""
    user_id = request.get_cookie('wmUserID')
    title = request.forms.get('mark_title')
    url = request.forms.get('mark_url')
    
    if not title or not url:
        return render_main_view(user_id, Error(151))
    
    # Check for duplicates
    if BookmarkManager.check_duplicate(user_id, url):
        logger.info(f"Duplicate bookmark detected for user {user_id}: {url}")
        return render_main_view(user_id, Error(150))
    
    # Insert bookmark
    try:
        BookmarkManager.insert_bookmark(user_id, title, url)
        return render_main_view()
    except Exception:
        return render_main_view(user_id, Error(2000))


@app.post("/ex2WebMarks/updateMark")
@app.post("/updateMark")
@authenticate
def update_mark():
    """Update existing bookmark."""
    user_id = request.get_cookie('PYwmUserID')
    title = request.forms.get('title_update')
    url = request.forms.get('url_update')
    bookmark_id = request.params['bk_id']
    
    try:
        BookmarkManager.update_bookmark(bookmark_id, title, url)
        return render_main_view()
    except Exception:
        return render_main_view(user_id, Error(153))


@app.post("/ex2WebMarks/deleteMark")
@app.post("/deleteMark")
@authenticate
def delete_mark():
    """Delete bookmark."""
    user_id = request.get_cookie('wmUserID')
    bookmark_id = request.params['bk_id']
    
    try:
        BookmarkManager.delete_bookmark(bookmark_id)
        return render_main_view()
    except Exception:
        return render_main_view(user_id, Error(153))


@app.post("/ex2WebMarks/deltaPass")
@app.post("/deltaPass")
@authenticate
def change_password():
    """Change user password."""
    username = util.unWrap(request, 'user_name')
    old_password = util.unWrap(request, 'old_user_pass')
    new_password = util.unWrap(request, 'user_pass')
    
    # Verify old password
    auth_result = UserAuth.authenticate_user(username, old_password, old_password)
    
    if not auth_result:
        return render_main_view(username, Error(112))
    
    user_id = auth_result[0]
    
    # Update password
    if UserAuth.update_password(username, new_password):
        return render_main_view()
    else:
        return render_main_view(user_id, Error(102))


# Error handlers
@app.error(404)
def error_404(error):
    """Handle 404 errors."""
    return Marks().renderErrorPageView()


# Application entry point
if __name__ == '__main__':
    app.run(
        daemon=True,
        debug=False,
        host="0.0.0.0",
        port='8089',
        reloader=True,
        server='gunicorn',
        workers=3
    )
