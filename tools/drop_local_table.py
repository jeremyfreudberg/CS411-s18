import boto3

dynamo = boto3.resource('dynamodb',
                        endpoint_url='http://localhost:8000',
                        region_name='dummy',
                        aws_access_key_id='dummy',
                        aws_secret_access_key='dummy')

t = dynamo.Table('CS411')
t.delete()

t = dynamo.Table('WeatherRecipes')
t.delete()
