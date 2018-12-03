import requests
import boto3
import botocore
import sys
import json
import random
from weatherfood import application


app = application.app
API_KEY = app.config['API_KEY']
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?zip={0},us&appid={1}"
RESULT_BASE = "{0}, and {1} degrees Fahrenheit"

USE_LOCAL_DYNAMO = bool(app.config['USE_LOCAL_DYNAMO'])
def _load_dynamo_resource():
    if not USE_LOCAL_DYNAMO:
        return boto3.resource('dynamodb')
    else:
        return boto3.resource('dynamodb',
                              endpoint_url='http://localhost:8000',
                              region_name='dummy',
                              aws_access_key_id='dummy',
                              aws_secret_access_key='dummy')

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

#Function that takes in a single value search query from input and creates a Recipe Puppy API Query
#returns a dictionary with key = recipe title, value = recipe http address
def Recipe_from_input(recipe):
	http_address = 'http://www.recipepuppy.com/api/?q='
	dicto = {}

	try:
		content = requests.get(http_address + recipe)
	except TypeError:
		return None

	for result in content.json()['results']:		
		#dicto.update( {temp : result['href']} )
		dicto.update( {result['title'] :result['href']} )

	#return content.json()
	#print(dicto)
	return dicto

#Function that creates a new user and puts it in our DynamoDB database
def create_user(UserName):
	dynamodb = _load_dynamo_resource()
	table = dynamodb.Table('CS411')
	try:
		table.put_item(
			Item={
				'Username': UserName,
				'Zipcode': 0,
				'Weather': None,
				'Fav_Recipes': []
			},
			ConditionExpression='attribute_not_exists(Username)'
		)
	except botocore.exceptions.ClientError as e:
		# Ignore the ConditionalCheckFailedException, bubble up
		# other exceptions.
		if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
			raise

#Function that retrieves user through their user name
def retreive_user(UserName):
	dynamodb = _load_dynamo_resource()
	table = dynamodb.Table('CS411')
	try:
		response = table.get_item(
			Key={
				'Username': UserName
			}
		)
		item = response['Item']
		return item
	except KeyError:
		return None

#Function that updates a user's zipcode
def update_zipcode(UserName, Zipcode):
	dynamodb = _load_dynamo_resource()
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
	dynamodb = _load_dynamo_resource()
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
	dynamodb = _load_dynamo_resource()
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

	dynamodb = _load_dynamo_resource()
	table = dynamodb.Table('CS411')
	table.update_item(
		Key={
			'Username': UserName
		},
		UpdateExpression='REMOVE Fav_Recipes[{}]'.format(index),
		ReturnValues = "UPDATED_NEW"
	)

#Function that retrieves a random recipe look-up name from a table based off of temperature
def grab_temp_recipe(Temperature):
	key =""
	if Temperature <= 50:
		key = "low"
	elif Temperature >= 75:
		key = "high"
	else:
		key = "medium"

	dynamodb = _load_dynamo_resource()
	table = dynamodb.Table('WeatherRecipes')
	try:
		response = table.get_item(
			Key={
				'Temperature': key
			}
		)
		item = response['Item']
		#return item
	except KeyError:
		return None
	
	recipes = []
	recipes = item["Recipes"]
	index = random.randint(0,len(recipes))
	print(index)
	print("\n")

	return recipes[index]