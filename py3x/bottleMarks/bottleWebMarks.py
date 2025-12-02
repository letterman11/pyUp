
"""
Webmarks Application - Bookmark Management System
A Bottle-based web application for managing and syncing bookmarks.
author: angus brooks -- refactored and cleaned by ai
"""

from bottle import Bottle, request, response, static_file, error
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Tuple
import time
import re
import logging

from marks import Marks
from PJJExecPageSQL import exec_page
import lib.util_db as util
import connection_factory as db
from error import Error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize application
app = Bottle()
APP_COOKIE_PATH = "/pyWebMarks"
COOKIE_EXPIRY_DAYS = 5

# Database placeholder for parameterized queries
PLACE = db.db_factory().place


#----------------------------------------------------------#
# Static File Routes
#----------------------------------------------------------#

@app.route('/public/css/<filename>')
@app.route('/static/css/<filename>')
def serve_static_css(filename):
    """Serve CSS files (ideally use Nginx/Apache in production)."""
    return static_file(filename, root="./public/css")


@app.route('/public/images/<filename>')
@app.route('/static/images/<filename>')
def serve_static_images(filename):
    """Serve image files."""
    return static_file(filename, root="./public/images")


@app.route('/public/js/<filename>')
@app.route('/static/js/<filename>')
def serve_static_js(filename):
    """Serve JavaScript files."""
    return static_file(filename, root="./public/js")


#----------------------------------------------------------#
# Authentication & Authorization
#----------------------------------------------------------#

def authenticate(f):
    """Decorator to protect routes requiring authentication."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not validate_session(request):
            logger.warning("Unauthorized access attempt")
            return Marks().renderDefaultView()
        return f(*args, **kwargs)
    return wrapper


def validate_session(req) -> bool:
    """Validate user session from database."""
    return util.validateSessionDB(req)


def authenticate_user(username: str, password: str, old_password: Optional[str] = None) -> Optional[Tuple[str, str, str]]:
    """
    Authenticate user credentials.
    
    Args:
        username: User's username
        password: User's password
        old_password: Old password (for password changes)
    
    Returns:
        Tuple of (user_id, username, password) if valid, None otherwise
    """
    if not username or not password:
        return None
    
    password_digest = util.digest_pass(password)
    old_password_digest = util.digest_pass(old_password) if old_password else None
    
    query = "SELECT user_id, user_name, user_passwd FROM WM_USER WHERE user_name = {}".format(PLACE)
    
    try:
        conn = db.db_factory().connect()
        cursor = conn.cursor()
        cursor.execute(query, (username,))
        db_row = cursor.fetchall()
        conn.close()
        
        if not db_row:
            return None
        
        db_user_id, db_username, db_password_hash = db_row[0]
        
        # Check if old password matches (for password changes)
        if old_password and (db_password_hash == old_password or db_password_hash == old_password_digest):
            return (db_user_id, db_username, password)
        
        # Check if current password matches
        if db_password_hash == password or db_password_hash == password_digest:
            return (db_user_id, db_username, db_password_hash)
        
        return None
        
    except Exception as ex:
        logger.error(f"Authentication error: {ex}")
        return None


def create_session(user_id: str, username: str):
    """Create user session and set cookies."""
    session_id = util.genSessionID()
    expiry_timestamp = int(time.time()) + (60 * 60 * 24 * COOKIE_EXPIRY_DAYS)
    
    response.set_cookie('wmSessionID', str(session_id), path=APP_COOKIE_PATH, expires=expiry_timestamp)
    response.set_cookie('wmUserID', str(user_id), path=APP_COOKIE_PATH, expires=expiry_timestamp)
    response.set_cookie('wmUserName', str(username), path=APP_COOKIE_PATH, expires=expiry_timestamp)
    response.set_cookie('Counter', '0', path=APP_COOKIE_PATH, expires=expiry_timestamp)
    
    util.saveSessionDB(session_id, user_id)
    logger.info(f"Session created for user: {username}")


#----------------------------------------------------------#
# Database Helper Functions
#----------------------------------------------------------#

def get_max_ids(cursor) -> Tuple[int, int]:
    """Get maximum bookmark and place IDs."""
    cursor.execute("SELECT MAX(BOOKMARK_ID) FROM WM_BOOKMARK")
    bookmark_id = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT MAX(PLACE_ID) FROM WM_PLACE")
    place_id = cursor.fetchone()[0] or 0
    
    return bookmark_id + 1, place_id + 1


def check_duplicate_bookmark(cursor, user_id: str, url: str) -> bool:
    """Check if bookmark already exists for user."""
    query = """
        SELECT b.url FROM WM_BOOKMARK a, WM_PLACE b 
        WHERE a.PLACE_ID = b.PLACE_ID AND a.USER_ID = {} AND b.URL = {}
    """.format(PLACE, PLACE)
    
    cursor.execute(query, (user_id, url))
    return cursor.fetchone() is not None


def get_place_id_for_bookmark(cursor, bookmark_id: str) -> Optional[int]:
    """Get place_id for a given bookmark_id."""
    query = "SELECT PLACE_ID FROM WM_BOOKMARK WHERE BOOKMARK_ID = {}".format(PLACE)
    cursor.execute(query, (bookmark_id,))
    result = cursor.fetchone()
    return result[0] if result else None


#----------------------------------------------------------#
# Public Routes
#----------------------------------------------------------#

@app.route("/pyWebMarks/registration")
@app.route('/registration')
def register():
    """Display registration page."""
    return Marks().renderRegistrationView()


@app.post("/pyWebMarks/regAuth")
@app.post('/regAuth')
def register_user():
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
    
    if len(password1) < 6:
        return Marks().renderRegistrationView(Error(111).errText())
    
    if not re.match(r"^[a-zA-Z0-9\.]+@[a-zA-Z0-9\.]+", email):
        return Marks().renderRegistrationView(Error(119).errText())
    
    # Generate user ID
    part_id = util.genSessionID()[0:5]
    user_id = f"{username[0:5]}_{part_id}"
    
    # Hash password
    password_hash = util.digest_pass(password1)
    
    # Insert user
    insert_query = "INSERT INTO WM_USER (USER_ID, USER_NAME, USER_PASSWD, EMAIL_ADDRESS) VALUES ({},{},{},{})".format(
        PLACE, PLACE, PLACE, PLACE
    )
    
    try:
        conn = db.db_factory().connect()
        cursor = conn.cursor()
        conn.autocommit = False
        
        cursor.execute(insert_query, (user_id, username, password_hash, email))
        conn.commit()
        
        logger.info(f"New user registered: {username}")
        return Marks().renderDefaultView("red", f"Successfully Registered {username}")
        
    except Exception as ex:
        logger.error(f"Registration error: {ex}")
        conn.rollback()
        return Marks().renderRegistrationView(Error(120).errText())
    finally:
        conn.close()


@app.route("/pyWebMarks/default")
@app.route('/default')
def login():
    """Display login page."""
    return Marks().renderDefaultView()


@app.route("/pyWebMarks/logout")
@app.route("/logout")
def logout():
    """Log out user."""
    return Marks().renderDefaultView()


@app.route("/authenCred", method=['GET', 'POST'])
@app.route("/pyWebMarks/authenCred", method=['GET', 'POST'])
def authenticate_credentials():
    """Authenticate user credentials and create session."""
    username = util.unWrap(request, 'user_name')
    password = util.unWrap(request, 'user_pass')
    old_password = util.unWrap(request, 'old_user_pass')
    
    auth_result = authenticate_user(username, password, old_password)
    
    if auth_result:
        user_id, username, _ = auth_result
        create_session(user_id, username)
        return render_main_view(user_id)
    else:
        return Marks().renderDefaultView(
            colorStyle="red",
            displayText=Error(112).errText()
        )


@app.error(404)
def error_404(error):
    """Handle 404 errors."""
    return Marks().renderErrorPageView()


#----------------------------------------------------------#
# Authenticated Routes
#----------------------------------------------------------#

@app.route("/pyWebMarks")
@app.route("/")
@authenticate
def index():
    """Main application page."""
    return render_main_view()


@app.route("/pyWebMarks/webMarks")
@app.route("/webMarks")
@authenticate
def webmarks():
    """Webmarks view."""
    return render_main_view()


@app.route("/pyWebMarks/tabView")
@app.route("/tabView")
@authenticate
def tab_view():
    """Tab view."""
    return render_main_view()


@app.post("/pyWebMarks/searchMark")
@app.post("/searchMark")
@authenticate
def search_bookmark():
    """Search bookmarks."""
    return render_main_view()


@app.post("/pyWebMarks/insertMark")
@app.post("/insertMark")
@authenticate
def add_bookmark():
    """Add new bookmark."""
    user_id = request.get_cookie('wmUserID')
    title = request.forms.get('mark_title', '').strip()
    url = request.forms.get('mark_url', '').strip()
    
    if not title or not url:
        return render_main_view(user_id, Error(151))
    
    # Generate timestamp
    unix_timestamp = int(time.time())
    year, mon, day, hour, mins, secs = time.localtime(unix_timestamp)[0:6]
    date_string = f'{year}-{mon}-{day} {hour}:{mins}:{secs}'
    
    try:
        conn = db.db_factory().connect()
        cursor = conn.cursor()
        conn.autocommit = False
        
        # Get next IDs
        bookmark_id, place_id = get_max_ids(cursor)
        
        # Check for duplicates
        if check_duplicate_bookmark(cursor, user_id, url):
            logger.warning(f"Duplicate bookmark attempt: {url}")
            return render_main_view(user_id, Error(150))
        
        # Insert into WM_PLACE
        cursor.execute(
            "INSERT INTO WM_PLACE (PLACE_ID, URL, TITLE) VALUES ({},{},{})".format(PLACE, PLACE, PLACE),
            (place_id, url, title)
        )
        
        # Insert into WM_BOOKMARK
        cursor.execute(
            "INSERT INTO WM_BOOKMARK (BOOKMARK_ID, USER_ID, PLACE_ID, TITLE, DATEADDED, DATE_ADDED) VALUES ({},{},{},{},{},{})".format(
                PLACE, PLACE, PLACE, PLACE, PLACE, PLACE
            ),
            (bookmark_id, user_id, place_id, title, unix_timestamp, date_string)
        )
        
        conn.commit()
        logger.info(f"Bookmark added: {title} by user {user_id}")
        
    except Exception as ex:
        logger.error(f"Error adding bookmark: {ex}")
        conn.rollback()
        return render_main_view(user_id, Error(2001))
    finally:
        conn.close()
    
    return render_main_view()


@app.post("/pyWebMarks/updateMark")
@app.post("/updateMark")
@authenticate
def update_bookmark():
    """Update existing bookmark."""
    user_id = request.get_cookie('wmUserID')
    title = request.forms.get('title_update', '').strip()
    url = request.forms.get('url_update', '').strip()
    bookmark_id = request.params.get('bk_id')
    
    if not bookmark_id:
        return render_main_view(user_id, Error(153))
    
    try:
        conn = db.db_factory().connect()
        cursor = conn.cursor()
        conn.autocommit = False
        
        # Get place_id
        place_id = get_place_id_for_bookmark(cursor, bookmark_id)
        if not place_id:
            return render_main_view(user_id, Error(153))
        
        # Update bookmark and place
        cursor.execute(
            "UPDATE WM_BOOKMARK SET TITLE = {} WHERE BOOKMARK_ID = {}".format(PLACE, PLACE),
            (title, bookmark_id)
        )
        cursor.execute(
            "UPDATE WM_PLACE SET URL = {}, TITLE = {} WHERE PLACE_ID = {}".format(PLACE, PLACE, PLACE),
            (url, title, place_id)
        )
        
        conn.commit()
        logger.info(f"Bookmark updated: {bookmark_id}")
        
    except Exception as ex:
        logger.error(f"Error updating bookmark: {ex}")
        conn.rollback()
        return render_main_view(user_id, Error(153))
    finally:
        conn.close()
    
    return render_main_view()


@app.post("/pyWebMarks/deleteMark")
@app.post("/deleteMark")
@authenticate
def delete_bookmark():
    """Delete bookmark."""
    user_id = request.get_cookie('wmUserID')
    bookmark_id = request.params.get('bk_id')
    
    if not bookmark_id:
        return render_main_view(user_id, Error(153))
    
    try:
        conn = db.db_factory().connect()
        cursor = conn.cursor()
        conn.autocommit = False
        
        # Get place_id
        place_id = get_place_id_for_bookmark(cursor, bookmark_id)
        if not place_id:
            return render_main_view(user_id, Error(153))
        
        # Delete from both tables
        cursor.execute(
            "DELETE FROM WM_PLACE WHERE PLACE_ID = {}".format(PLACE),
            (place_id,)
        )
        cursor.execute(
            "DELETE FROM WM_BOOKMARK WHERE BOOKMARK_ID = {}".format(PLACE),
            (bookmark_id,)
        )
        
        conn.commit()
        logger.info(f"Bookmark deleted: {bookmark_id}")
        
    except Exception as ex:
        logger.error(f"Error deleting bookmark: {ex}")
        conn.rollback()
        return render_main_view(user_id, Error(153))
    finally:
        conn.close()
    
    return render_main_view()


@app.post("/pyWebMarks/deltaPass")
@app.post("/deltaPass")
@authenticate
def change_password():
    """Change user password."""
    username = util.unWrap(request, 'user_name')
    password = util.unWrap(request, 'user_pass')
    old_password = util.unWrap(request, 'old_user_pass')
    
    auth_result = authenticate_user(username, password, old_password)
    
    if not auth_result:
        return render_main_view(username, Error(112))
    
    user_id, username, _ = auth_result
    new_password = request.params.get('user_pass')
    new_password_hash = util.digest_pass(new_password)
    
    try:
        conn = db.db_factory().connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE WM_USER SET USER_PASSWD = {} WHERE USER_NAME = {}".format(PLACE, PLACE),
            (new_password_hash, username)
        )
        conn.commit()
        
        logger.info(f"Password changed for user: {username}")
        
    except Exception as ex:
        logger.error(f"Error changing password: {ex}")
        return render_main_view(user_id, Error(102))
    finally:
        conn.close()
    
    return render_main_view()


#----------------------------------------------------------#
# View Rendering
#----------------------------------------------------------#

def render_main_view(user_id: Optional[str] = None, err_obj: Optional[Error] = None):
    """Render the main application view."""
    username = request.params.get('user_name')
    
    if not user_id or not username:
        user_id = request.get_cookie('wmUserID')
        username = request.get_cookie('wmUserName')
    
    return exec_page(request, user_id, username, err_obj)


#----------------------------------------------------------#
# Application Entry Point
#----------------------------------------------------------#

if __name__ == '__main__':
    app.run(
        daemon=True,
        debug=False,
        host="0.0.0.0",
        port=8096,
        reloader=True,
        server='gunicorn',
        workers=3
    )
