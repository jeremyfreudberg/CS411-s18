import boto3

dynamo = boto3.resource('dynamodb',
                        endpoint_url='http://localhost:8000',
                        region_name='dummy',
                        aws_access_key_id='dummy',
                        aws_secret_access_key='dummy')

dynamo.create_table(TableName='CS411',
                    KeySchema=[{'AttributeName': 'Username', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'Username', 'AttributeType': 'S'}],
                    ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
