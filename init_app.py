import os
from flask import Flask
from flask_dynamo import Dynamo
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.secret_key = os.environ.get("SECRET_KEY") 

    app.config['DYNAMO_TABLES'] = [{
        'TableName': 'users',
        'KeySchema': [{
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }],
        'AttributeDefinitions': [{
            'AttributeName': 'id',
            'AttributeType': 'S'
        }],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
        }, {
            'TableName': 'days',
            'KeySchema': [{
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }],
            'AttributeDefinitions': [{
                'AttributeName': 'id',
                'AttributeType': 'N'
            }],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }, {
            'TableName': 'cities',
            'KeySchema': [{
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }],
            'AttributeDefinitions': [{
                'AttributeName': 'id',
                'AttributeType': 'N'
            }],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
        }
    }, {
            'TableName': 'config',
            'KeySchema': [{
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }],
            'AttributeDefinitions': [{
                'AttributeName': 'id',
                'AttributeType': 'S'
            }],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
        }
    }]
    dynamo = Dynamo()
    dynamo.init_app(app)

    return app, dynamo
