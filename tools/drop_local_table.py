import boto3

dynamo = boto3.resource('dynamodb',
                        endpoint_url='http://localhost:8000',
                        region_name='dummy',
                        aws_access_key_id='dummy',
                        aws_secret_access_key='dummy')

tables = ['CS411', 'WeatherRecipes', 'YelpCache']
for table_name in tables:
    t = dynamo.Table(table_name)
    try:
        t.delete()
    except:
        pass
