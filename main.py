from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import user_management as dbHandler

#rate limits
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#encryption
from hash import *
from data_handler import *

#2fa
import pyotp
import qrcode
import os
import base64
from io import BytesIO

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
#limit requests
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
#2fa
app.secret_key = 'my_secret_key'



@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")


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
            print("weak password")
            return render_template("/weak_password.html") 
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
@limiter.limit("5 per minute")  # Add this line to limit login attempts
def home():
    user_secret = pyotp.random_base32() #generate the one-time passcode
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            totp = pyotp.TOTP(user_secret)
            otp_uri = totp.provisioning_uri(name=username,issuer_name="NormoUnsecurePWA")
            qr_code = qrcode.create(otp_uri)
            stream = BytesIO()
            qr_code.png(stream, scale=5)
            qr_code_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')
            dbHandler.listFeedback()
            return render_template("/enable_2fa.html")
            
            #return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")

@app.route('/enable_2fa.html', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def enable_2fa():
    if request.method == 'POST':
        otp_input = request.form['otp']
        if totp.verify(otp_input):
            return render_template('success.html')
            #return redirect(url_for('home'))  # Redirect to home if OTP is valid
        else:
            return "Invalid OTP. Please try again.", 401


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5001)
