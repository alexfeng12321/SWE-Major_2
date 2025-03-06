from flask import Flask
from flask import request
from flask import redirect
from flask import session
import user_management as dbHandler

#CSRF Protection
from flask_wtf.csrf import CSRFProtect

#rate limits
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#encryption
from hash import *
from data_handler import *

#2fa
import pyotp
from qrcode import QRCode
import os
import base64
from io import BytesIO
from flask import render_template

    #sql injection using sql perameters 


# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)

#CSRF Protection
csrf = CSRFProtect(app)


#limit requests
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

#2fa
#code needs inital secret key setup
app.secret_key = 'my_secret_key'


'''
ALLOWED_URLS = [
    "/",
    "/index.html",
    "/signup.html",
    "/success.html",
    "/enable_2fa.html"
]

def is_safe_url(target):
    from urllib.parse import urlparse, urljoin
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc and target in ALLOWED_URLS
'''


app.config['SESSION_COOKIE_SAMESITE'] = 'strict'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes


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
    #response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers.pop('Server', None)
    return response




@app.route("/success.html", methods=["POST", "GET"])
@csrf.exempt
@limiter.limit("50 per minute")
def addFeedback():
    if session.get('username') is None:
        return redirect("/index.html")
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
        dbHandler.listFeedback()
        render_success = render_template("partials/success_feedback.html")
        render_feedback = render_template("/success.html", state=True, value=session.get('username'))
        return render_feedback + render_success
        #return render_template("/success.html", state=True, value=session.get('username'))
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value=session.get('username'))

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
            return render_template("/index.html")   
        else:
            return render_template("/weak_password.html") 
    else:
        return render_template("/signup.html")
'''


@app.route("/signup.html", methods=["POST", "GET"])
@limiter.limit("50 per minute")
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            check_password(password)
            DoB = request.form["dob"]
            password = encode(password)
            dbHandler.insertUser(username, password, DoB)
            return render_template("/index.html")
        except (TypeError, ValueError) as e:
            return render_template("/signup.html", error=str(e))
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
@limiter.limit("50 per minute")  # Add this line to limit login attempts
def home():
    user_secret = pyotp.random_base32() #generate the one-time passcode
    session['user_secret'] = user_secret 
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        session['username'] = username
        session['password'] = password
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
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
            return render_template("/index.html")
    else:
        return render_template("/index.html")


@app.route('/enable_2fa.html', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
@csrf.exempt
def enable_2fa():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == 'POST' :
        otp_input = request.form['otp']
        user_secret = session.get('user_secret')
        if user_secret:
            totp = pyotp.TOTP(user_secret)
            if totp.verify(otp_input):
                return render_template('/success.html', value=session.get('username'), state=True)
            else:
                return "Invalid OTP. Please try again.", 401
        else:
            return "Invalid OTP. Please try again.", 401

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Clear the session data
    return redirect("/index.html")



if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5001)
    #app.run(debug=True, host="0.0.0.0", port=5001, ssl_context="adhoc")



