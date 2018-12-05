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

dynamo.create_table(TableName='WeatherRecipes',
                    KeySchema=[{'AttributeName': 'Temperature', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'Temperature', 'AttributeType': 'S'}],
                    ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})

COLD_TEMP_RECIPES = ['lasagna',
                     'roast chicken',
                     'hot soup',
                     'dumplings',
                     'spaghetti',
                     'fried chicken',
                     'goulash',
                     'cajun pork',
                     'potatoes',
                     'casserole',
                     'bread pudding',
                     'meatballs',
                     'mac and cheese',
                     'beef roast',
                     'pork chops',
                     'mashed potatoes',
                     'apple cake',
                     'pork roast',
                     'pot roast',
                     'gingerbread cake',
                     'lamb stew',
                     'skillet',
                     'minestrone']

MEDIUM_TEMP_RECIPES = ['butternut squash',
                       'lemon chicken',
                       'enchiladas',
                       'meat sauce',
                       'chili chicken',
                       'roast beef',
                       'chili',
                       'alfredo',
                       'penne',
                       'sausage soup',
                       'cottage pie',
                       'chicken and biscuits',
                       'pea soup',
                       'chicken with potatoes',
                       'mexican lasagna',
                       'goat cheese',
                       'pot pie',
                       'meatloaf',
                       'salmon',
                       'rice',
                       'beans',
                       'quesadillas',
                       'burrito']

HIGH_TEMP_RECIPES = ['caprese salad',
                     'kale salad',
                     'spring rolls',
                     'pad thai',
                     'poke bowl',
                     'couscous salad',
                     'pasta salad',
                     'ice cream',
                     'popsicle',
                     'chickpea salad',
                     'mochi',
                     'quinoa salad',
                     'blt',
                     'sub',
                     'burger',
                     'hot dog',
                     'chicken bites',
                     'flatbread',
                     'orzo',
                     'lettuce',
                     'shrimp',
                     'yogurt',
                     'gazpacho',
                     'sorbet']

t = dynamo.Table('WeatherRecipes')
t.put_item(
    Item={'Temperature': 'low', 'Recipes': COLD_TEMP_RECIPES}
)
t.put_item(
    Item={'Temperature': 'medium', 'Recipes': MEDIUM_TEMP_RECIPES}
)
t.put_item(
    Item={'Temperature': 'high', 'Recipes': HIGH_TEMP_RECIPES}
)
