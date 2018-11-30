import flask
from weatherfood import api
from weatherfood import application

app = application.app
google = application.google_login

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

@app.route('/', methods=['POST'])
def weather():
    current_weather = api.get_weather_pretty(
        flask.request.form.get("zipcode"))
    return flask.render_template('result.html', weather=current_weather)

@app.route('/login_test', methods=['GET'])
def login():
    return '<a href="{}">Login with Google</a>'.format(
        google.authorization_url())

@google.login_success
def login_success(token, profile):
    return flask.jsonify(token=token, profile=profile)

@google.login_failure
def login_failure(e):
    return flask.jsonify(error=str(e))
