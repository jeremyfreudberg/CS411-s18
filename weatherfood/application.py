import flask
import flask_bootstrap

app = flask.Flask(__name__)
app.config.from_object('config')

flask_bootstrap.Bootstrap(app)
