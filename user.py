import json
import os
import uuid

import decimalencoder
import logging
import time
import boto3
dynamodb = boto3.resource('dynamodb')


def list(event, context):
    table = dynamodb.Table(os.environ['user_table'])

    # fetch all todos from the database
    result = table.scan()
    logging.info(result)

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(result['Items'], cls=decimalencoder.DecimalEncoder)
    }

    return response


def create(event, context):
    table = dynamodb.Table(os.environ['user_table'])

    data = json.loads(event['body'])
    print("after data dump", type(data))

    name = data['name']
    print("name", name)
    password = data['password']
    print("password", password)

    if not name or not password:
        print("In if")
        logging.error("username or password empty. ")
        raise Exception("Couldn't create the todo item.")

    timestamp = int(time.time() * 1000)

    item = {
        "user_id": str(uuid.uuid1()),
        "name": name,
        "password": password,
        "created_at": timestamp
    }
    print("item", item)

    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "user_id": str(item['user_id'])
        })
    }

    print(type(response), response)
    return response


def login(event, context):
    print("event", event)
    table = dynamodb.Table(os.environ['user_table'])

    data = json.loads(event['body'])
    print("after data dump", type(data))

    user_id = data['user_id']
    print("name", user_id)
    password = data['password']
    print("password", password)

    if not user_id or not password:
        print("In if")
        logging.error("username or password empty. ")
        raise Exception("Couldn't create the todo item.")

    result = table.get_item(
        Key={
            'user_id': str(user_id)
        }
    )

    print(type(result), result)

    if not result:
        response = {
            "statusCode": 400,
            "body": json.dumps({"message":"Incorrect user_id"})
        }
        return response

    print("password", result['Item']['password'])

    if password != result['Item']['password']:
        response = {
            "statusCode": 400,
            "body": json.dumps({"message": "Incorrect password"})
        }
        return response

    response = {
            "statusCode": 200,
            "body": json.dumps({"user_id": str(user_id)})
        }
    return response
