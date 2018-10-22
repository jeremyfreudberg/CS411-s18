import flask
from weatherfood import api
from weatherfood import application

app = application.app

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

@app.route('/', methods=['POST'])
def weather():
    current_weather = api.get_weather_pretty(
        flask.request.form.get("zipcode"))
    return flask.render_template('result.html', weather=current_weather)
