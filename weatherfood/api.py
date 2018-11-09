import requests
import boto3
import sys
import json
#from weatherfood import application

'''
app = application.app
API_KEY = app.config['API_KEY']
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?zip={0},us&appid={1}"
RESULT_BASE = "{0}, and {1} degrees Fahrenheit"
'''

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

#Function that creates a new user and puts it in our DynamoDB database
def create_user(UserName, Zipcode):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('CS411')
	table.put_item(
		Item={
			'Username': UserName,
			'Zipcode': Zipcode,
			'Weather': None,
            'Fav_Recipes': None
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
