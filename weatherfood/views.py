import flask
from weatherfood import api
from weatherfood import application

app = application.app
google = application.google_login

@app.route('/home', methods=['GET'])
def index():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    msg = None
    if flask.request.args.get('error', None):
        msg = "<font color=red>Can't fetch weather. Was that a valid zipcode?</font><br />"
    return flask.render_template('index.html', msg=msg)

@app.route('/weather', methods=['GET','POST'])
def weather():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')

    zipcode = flask.request.form.get('zipcode')
    current_weather = api.get_weather_pretty(zipcode)
    if current_weather == "Unavailable":
        current_weather = api.retreive_user(username)["Weather"]
        # Attempt to use the cached zipcode:
        zipcode = api.retreive_user(username)["Zipcode"]
    else:
        api.update_zipcode(username, zipcode)
        api.update_weather(username, current_weather)

    if zipcode:
        return flask.render_template('result.html', weather=current_weather, zipcode=zipcode)
    else:
        # The user entered an invalid ZIP, and never previously entered a valid ZIP during a prior session
        return flask.redirect('/home?error=1')

@app.route('/', methods=['GET'])
def login():
    return flask.render_template('home.html', url=google.authorization_url(), hide_logout=True)

@google.login_success
def login_success(token, profile):
    result = flask.jsonify(token=token, profile=profile)
    username = result.get_json()["profile"]["email"]
    api.create_user(username)
    flask.session['username'] = username
    return flask.render_template('index.html')

@google.login_failure
def login_failure(e):
    return flask.jsonify(error=str(e))

@app.route('/logout')
def logout():
    flask.session['username'] = None
    return flask.redirect('/')

@app.route('/customrecipe', methods=['POST'])
def show_recipe():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    current_recipe = api.Recipe_from_input(
        flask.request.form.get("recipe"))
    return flask.render_template('custom_recipe.html', recipe=current_recipe)

@app.route('/process_favorites', methods=['POST'])
def add_favorite_recipes():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    data = flask.request.form.to_dict()
    data.pop('submit')
    if data:
        for name, url in data.items():
            api.update_recipe(username, name, url)
    return flask.redirect('/viewfavorites')

@app.route('/viewfavorites', methods=['GET'])
def show_favorites():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    return flask.render_template( 'favorites.html', favorites = api.retreive_user(username)["Fav_Recipes"] )

@app.route("/del_fav", methods=["POST"])
def delete_favorite():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    api.delete_favorite(username, flask.request.values.get('delete'))
    return flask.redirect('/viewfavorites')
