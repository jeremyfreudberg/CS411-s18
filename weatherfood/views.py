import flask
from weatherfood import api
from weatherfood import application

app = application.app
google = application.google_login
temp = {}

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

@app.route('/weather', methods=['GET','POST'])
def weather():

    if( api.get_weather_pretty(flask.request.form.get("zipcode")) != "Unavailable" ):
        current_weather = api.get_weather_pretty(
            flask.request.form.get("zipcode"))
    else:
        current_weather = api.retreive_user("Testo3")["Weather"]

    api.update_zipcode("Testo3", flask.request.form.get("zipcode"))
    api.update_weather("Testo3", current_weather)
    
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

@app.route('/customrecipe', methods=['POST'])
def show_recipe():
    current_recipe = api.Recipe_from_input(
        flask.request.form.get("recipe"))
    temp.clear()
    temp.update(current_recipe)
    return flask.render_template('custom_recipe.html', recipe=current_recipe)

@app.route('/viewfavorites', methods=['GET'])
def show_favorites():
    return flask.render_template( 'favorites.html', favorites = api.retreive_user("Testo3")["Fav_Recipes"] )

@app.route("/del_fav", methods=["GET"])
def delete_favorite():
    api.delete_favorite("Testo3", flask.request.values.get('delete'))
    return flask.render_template( 'favorites.html', favorites = api.retreive_user("Testo3")["Fav_Recipes"] )

@app.route('/fav_recipe', methods=['GET'])
def favorite_recipe():
    api.update_recipe("Testo3", flask.request.values.get('key'), flask.request.values.get('favorite') )
    return flask.render_template('custom_recipe.html', recipe=temp)
