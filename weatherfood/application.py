import flask
import flask_bootstrap
import flask_oauth2_login

app = flask.Flask(__name__)
app.config.from_object('config')

flask_bootstrap.Bootstrap(app)

google_login = flask_oauth2_login.GoogleLogin(app)
