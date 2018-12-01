import requests
import boto3
import sys
import json
from weatherfood import application


app = application.app
API_KEY = app.config['API_KEY']
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?zip={0},us&appid={1}"
RESULT_BASE = "{0}, and {1} degrees Fahrenheit"


def _kelvin_to_fahrenheit(k):
    f = (k * 1.8) - 459.67
    return int(f)

def get_weather_pretty(zipcode):
    raw = requests.post(BASE_URL.format(zipcode, API_KEY)).json()
    try:
        conditions = raw["weather"][0]["main"]
        temperature = _kelvin_to_fahrenheit(raw["main"]["temp"])
    except KeyError:
        return "Unavailable"
    else:
        return RESULT_BASE.format(conditions, temperature)

#http://www.recipepuppy.com/api/?i=onions,garlic&q=omelet&p=3 		

#Function that takes in ingredients from argv and creates a Recipe Puppy API Query
#returns a dictionary with key = recipe title, value = recipe http address
def Recipe_from_ingredients():
	ingredients = []
	http_address = 'http://www.recipepuppy.com/api/?i='
	dicto = {}

	for value in sys.argv[1:]:
		ingredients.append(value)

	for value in ingredients:
		if value != (ingredients[len(ingredients) - 1]):
			http_address += value + ','
		else:
			http_address += value

	content = requests.get(http_address)
	#print(http_address)	
	#print(content.json())

	for result in content.json()['results']:
		
		for char in json.dumps(result['title']):
			temp = ''
			try:
				if( (int(char) > 64 and int(char) < 91) or (int(char) > 96 and int(char) < 123) or (int(char) == 32) or (int(char) == 39) or (int(char) == 44) or (int(char) == 45) ):
					temp += char
			except ValueError:
				pass
			
		
		#dicto.update( {temp : result['href']} )
		dicto.update( {json.dumps(result['title']) : json.dumps(result['href'])} )

	#return content.json()
	print(dicto)
	return dicto

#Function that takes in a single value search query from argv and creates a Recipe Puppy API Query
#returns a dictionary with key = recipe title, value = recipe http address
def Recipe_from_query():
	http_address = 'http://www.recipepuppy.com/api/?q='
	dicto = {}

	content = requests.get(http_address + sys.argv[1])

	for result in content.json()['results']:
		'''
		for char in json.dumps(result['title']):
			temp = ''
			try:
				if( (int(char) > 64 and int(char) < 91) or (int(char) > 96 and int(char) < 123) or (int(char) == 32) or (int(char) == 39) or (int(char) == 44) or (int(char) == 45) ):
					temp += char
			except ValueError:
				pass
		'''	
		
		#dicto.update( {temp : result['href']} )
		dicto.update( {json.dumps(result['title']) : json.dumps(result['href'])} )

	#return content.json()
	print(dicto)
	return dicto

#Function that takes in a single value search query from input and creates a Recipe Puppy API Query
#returns a dictionary with key = recipe title, value = recipe http address
def Recipe_from_input(recipe):
	http_address = 'http://www.recipepuppy.com/api/?q='
	dicto = {}

	content = requests.get(http_address + recipe)

	for result in content.json()['results']:		
		#dicto.update( {temp : result['href']} )
		dicto.update( {json.dumps(result['title']) : json.dumps(result['href'])} )

	#return content.json()
	print(dicto)
	return dicto

#Function that creates a new user and puts it in our DynamoDB database
def create_user(UserName, Zipcode):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	table.put_item(
		Item={
			'Username': UserName,
			'Zipcode': Zipcode,
			'Weather': None,
            'Fav_Recipes': []
		}
	)

#Function that retrieves user through their user name
def retreive_user(UserName):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	try:
		response = table.get_item(
			Key={
				'Username': UserName
			}
		)
		item = response['Item']
		return item
	except KeyError as e:
		return None

#Function that updates a user's zipcode
def update_zipcode(UserName, Zipcode):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	table.update_item(
		Key={
			'Username': UserName
		},
		UpdateExpression='SET Zipcode = :Zipcode',
		ExpressionAttributeValues={
			':Zipcode': Zipcode
		}
	)

#Function that updates a user's weather
def update_weather(UserName, Weather):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	table.update_item(
		Key={
			'Username': UserName
		},
		UpdateExpression='SET Weather = :Weather',
		ExpressionAttributeValues={
			':Weather': Weather
		}
	)

#Function that updates a user's favorite recipes
def update_recipe(UserName, RecipeKey, RecipeValue):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	table.update_item(
		Key={
			'Username': UserName
		},
		UpdateExpression='SET Fav_Recipes = list_append(Fav_Recipes, :Fav_Recipes)',
		ExpressionAttributeValues={
			':Fav_Recipes': [{str(RecipeKey) : str(RecipeValue)}]
		},
		ReturnValues = "UPDATED_NEW"
	)

#Function that deletes a user's favorite recipe
def delete_favorite(UserName, RecipeKey):
	count = 0
	index = 0

	for key in retreive_user(UserName)['Fav_Recipes']:
		if key == RecipeKey:
			index = count
		count+=1

	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	table.update_item(
		Key={
			'Username': UserName
		},
		UpdateExpression='REMOVE Fav_Recipes[{}]'.format(index),
		ReturnValues = "UPDATED_NEW"
	)
