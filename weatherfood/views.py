import flask
import requests
import datetime
import dateutil
import json
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
    zipcode = api.retreive_user(username)["Zipcode"]
    return flask.render_template('index.html', msg=msg, zipcode=zipcode)

@app.route('/weather', methods=['GET','POST'])
def weather():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')

    zipcode = flask.request.form.get('zipcode')
    current_recipe = api.Recipe_from_input(flask.request.form.get("recipe"))
    current_weather = api.get_weather_pretty(zipcode)
    temperature = 0
    if current_weather == "Unavailable":
        current_weather = api.retreive_user(username)["Weather"]

        if current_weather is None:
            return flask.redirect('/home?error=1')

        # Grabbing the temperature from the current_weather string
        for val in current_weather.split(): 
            if val.isdigit():
                temperature = int(val) 
        if current_recipe == None :
            current_recipe = api.Recipe_from_input(api.grab_temp_recipe(temperature))

        # Attempt to use the cached zipcode:
        zipcode = api.retreive_user(username)["Zipcode"]
    else:
        api.update_zipcode(username, zipcode)
        api.update_weather(username, current_weather)
        
        # Grabbing the temperature from the current_weather string
        for val in current_weather.split(): 
            if val.isdigit():
                temperature = int(val) 
        if current_recipe == None :
            current_recipe = api.Recipe_from_input(api.grab_temp_recipe(temperature))

    if zipcode:
        return flask.render_template('result.html', weather=current_weather, zipcode=zipcode, recipe=current_recipe)
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
    return flask.redirect('/home')

@google.login_failure
def login_failure(e):
    return flask.jsonify(error=str(e))

@app.route('/logout')
def logout():
    flask.session['username'] = None
    return flask.redirect('/')

@app.route('/process_favorites', methods=['POST'])
def add_favorite_recipes():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    data = flask.request.form.to_dict()
    data.pop('submit')
    existing_favorites = api.fetch_all_favorites(username)
    for fav in existing_favorites:
        data.pop(fav, None)
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

@app.route('/yelp', methods=['POST'])
def yelpform():
    username = flask.session.get('username', None)
    if username is None:
        return flask.redirect('/')
    zipcode = api.retreive_user(username)["Zipcode"]
    cached_results = api.retrieve_yelp_data(zipcode)
    now = datetime.datetime.now()
    fetch_new = False
    if cached_results is None:
        fetch_new = True
    else:
        difference = now - dateutil.parser.parse(cached_results['Updated'])
        if difference.seconds >= app.config['CACHE_EXPIRY_TIME']:
            fetch_new = True
    if fetch_new:
        URL = "https://api.yelp.com/v3/businesses/search"
        PARAMS={
	    'term': 'restaurants',
            'location': zipcode,
            'radius':2000
        }
        HEADERS={
            'Authorization': app.config['YELP_TOKEN']
        }
        r = requests.get(url = URL, params = PARAMS , headers = HEADERS)
        data = r.json()
        api.save_yelp_data(zipcode, r.content, now.isoformat())
    else:
        data = json.loads(cached_results['YelpData'])
    data = sorted(data['businesses'], key=lambda e: 'delivery' in e['transactions'], reverse=True)
    return flask.render_template('yelp.html', data=data, zipcode=zipcode)
