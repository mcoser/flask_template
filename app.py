from flask import Flask, request, Response, send_from_directory, url_for, render_template
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

app = Flask(__name__, static_folder='static')
app_port = 5050

# function for simple timestamped prints
# could also use https://flask.palletsprojects.com/en/2.0.x/logging/ though lol
def tsp(m):
    d = datetime.now()
    print(f"{d} - {m}")
    return

# rate limiting config - https://flask-limiter.readthedocs.io/en/stable/
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["2000 per day", "2000 per hour"]
)

# basic auth config - https://flask-httpauth.readthedocs.io/en/latest/
auth = HTTPBasicAuth()
users = {
    "admin": generate_password_hash("password"),
    "user": generate_password_hash("hunter1")
}

# basic auth decorator
@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/login', methods=['GET'])
@auth.login_required
def login():
    return "Hello, {}!".format(auth.current_user())

@app.route("/rate_limit", methods=['GET'])
@limiter.limit("10 per minute")
def rate_limit():
    tsp(f"HTTP Client: {request.remote_addr}")
    return('OK', 200)

@app.route('/test', methods=['POST'])
def test():
    tsp(f"/test endpoint hit!")
    return("OK", 200)

# returns a file for experimental purposes
# in prod, serve static files on the web server, not app 
@app.route('/file', methods=['GET'])
def send_file():
    return send_from_directory(app.static_folder, 'img/sand.jpg')

@app.route('/file/<path:filename>')  
def send_file_path(filename):  
    return send_from_directory(app.static_folder, filename)

@app.route('/html')  
def html():  
    return render_template("index.html")

# Failure endpoints, to test how an app handles certain HTTP responses. 
# Fails with 500
@app.route('/fail500', methods=['GET'])
def fail500():
    return("Server Error", 500)

# fails with custom code, if allowed. 
@app.route('/fail', methods=['GET'])
def fail():
    try:
        e = request.args.get('error')
        m = request.args.get('msg')
        return(str(m), int(e))
    except:
        return("Server Error", 500)


if __name__ == '__main__':
    # using host="0.0.0.0" allows app to be accessible using device IP over LAN, not just localhost
    # debug=True will restart the app every time a change is saved
    app.run(debug=True, port=app_port, host="0.0.0.0")
    print(f"Server listening on: http://localhost: {str(app_port)}")