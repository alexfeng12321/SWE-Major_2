from flask import Flask
from flask import request
from flask import redirect
from flask import session
from flask import render_template
import pyotp
import user_management as dbHandler

#CSRF Protection
from flask_wtf.csrf import CSRFProtect

#rate limits
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#encryption
from hash import *    

#data validation
from data_handler import *

#2fa
'''
import pyotp
from qrcode import QRCode
import os
import base64
from io import BytesIO
'''

# remove server header - doesnt work 
#from werkzeug.wrappers import Response
'''
class RemoveServerHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers = [(name, value) for name, value in headers if name.lower() != 'server']
            return start_response(status, headers, exc_info)
        return self.app(environ, custom_start_response)
        app.wsgi_app = RemoveServerHeaderMiddleware(app.wsgi_app)
'''
# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)

#CSRF Protection
csrf = CSRFProtect(app)

'''
#limit requests
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
'''


#2fa
#code needs inital secret key setup
app.secret_key = 'my_secret_key'


# external redirects -- bad
'''
ALLOWED_URLS = [
    "/",
    "/login.html",
    "/signup.html",
    "/success.html",
    "/enable_2fa.html",
    "/logout"
]
'''

'''
def is_safe_url(url):
    from urllib.parse import urlparse, urljoin
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc and url in ALLOWED_URLS
'''
'''
#cookie settings + other app configs
app.config['SESSION_COOKIE_SAMESITE'] = 'strict'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
app.config["TEMPLATES_AUTO_RELOAD"] = True
'''


@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self'; "
        "script-src 'self'; "
        "img-src 'self' data: ; "
        "media-src 'self'; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "frame-src 'none'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-cache', 'no-store'
    response.headers['pragma'] = 'no-cache'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    #response.headers.pop('Server', None)
    return response


@app.route("/login.html", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
#@limiter.limit("50 per minute")
@csrf.exempt
def login():
        return render_template('/home.html', code=302)
        '''
    return render_template("/home.html")

    user_secret = pyotp.random_base32() #generate the one-time passcode
    session['user_secret'] = user_secret 
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
        '''
        if is_safe_url(url):
            return redirect(url, code=302)
        else:
            return "invalid url", 400
        '''
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            dbHandler.listFeedback()
            return render_template("/home.html", value=username, state=isLoggedIn)
        else:
            return render_template("/login.html")
    else:
        return render_template("/login.html")
        '''
        username = request.form["username"]
        try:
            validate_name(username)
            password = request.form["password"]
            isLoggedIn = dbHandler.retrieveUsers(username, password)
            if isLoggedIn:
                session['username'] = username
                totp = pyotp.TOTP(user_secret)
                otp_uri = totp.provisioning_uri(name=username,issuer_name="NormoUnsecurePWA")
                qr = QRCode()
                qr.add_data(otp_uri)
                qr.make(fit=True)
                stream = BytesIO()
                qr.make_image(fill='black', back_color='white').save(stream)
                qr_code_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
                dbHandler.listFeedback()
                return render_template("/enable_2fa.html", qr_code=qr_code_b64)
            else:
                return render_template("/login.html")
        except (TypeError, ValueError) as e:
            return render_template("/login.html", error=str(e))
            '''
    
'''

@app.route("/home.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
#@limiter.limit("50 per minute")
@csrf.exempt
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)


@app.route("/success.html", methods=["POST", "GET"])
@csrf.exempt
#@limiter.limit("50 per minute")
def addFeedback():
    if session.get('username') is None:
        return redirect("/login.html")
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
        '''
        if is_safe_url(url):
            return redirect(url, code=302)
        else:
            return "invalid url", 400
            '''
    if request.method == "POST":
        feedback = request.form["feedback"]
        feedback = sanitise_feedback(feedback)
        try: 
            validate_feedback(feedback)
            dbHandler.insertFeedback(feedback)
            dbHandler.listFeedback()
            #debugging
            #feedback_list = dbHandler.listFeedback()
            #print(feedback_list)
            #render_success = render_template("partials/success_feedback.html")
            return render_template("/success.html", value=session.get('username'))
        except (TypeError, ValueError) as e:
            dbHandler.listFeedback()
            return render_template("/success.html", value=session.get('username'), error=str(e))
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=False, value=session.get('username'))


''' old code
@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if simple_check_password(password):
            DoB = request.form["dob"]
            password = encode(password)
            dbHandler.insertUser(username, password, DoB)
            return render_template("/login.html")   
        else:
            return render_template("/weak_password.html") 
    else:
        return render_template("/signup.html")
'''


@app.route("/signup.html", methods=["POST", "GET"])
#@limiter.limit("50 per minute")
@csrf.exempt
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
        '''
        if is_safe_url(url):
            return redirect(url, code=302)
        else:
            return "invalid url", 400
        '''
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]

        password = encode(password)
        dbHandler.insertUser(username, password, DoB)
        return render_template("/login.html")

        '''
        try:
            check_password(password)
            validate_name(username)
            DoB = request.form["dob"]
            password = encode(password)
            dbHandler.insertUser(username, password, DoB)
            return render_template("/login.html")
        except (TypeError, ValueError) as e:
            return render_template("/signup.html", error=str(e))
    '''
    else:
        return render_template("/signup.html")


@app.route('/enable_2fa.html', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
@csrf.exempt
def enable_2fa():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        redirect(url, code=302)
        
        #if is_safe_url(url):
        #    return redirect(url, code=302)
        #else:
        #    return "invalid url", 400
        
    if request.method == 'POST' :
        otp_input = request.form['otp']
        user_secret = session.get('user_secret')
        if user_secret:
            totp = pyotp.TOTP(user_secret)
            #if True:
            if totp.verify(otp_input):    
                return render_template('/success.html', value=session.get('username'), state=True)
            else:
                return "Invalid OTP. Please try again.", 401
        else:
            return "Invalid OTP. Please try again.", 401

            
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login.html")


if __name__ == "__main__":
    #app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    #app.run(debug=False, host="0.0.0.0", port=5001, ssl_context=('cert.pem', 'key.pem'))
    app.run(debug=True, host="0.0.0.0", port=5001)

