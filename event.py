import json
import os
import uuid

import decimalencoder
import logging
import time
import boto3

dynamodb = boto3.resource('dynamodb')


def create(event, context):
    event_table = dynamodb.Table(os.environ['event_table'])
    user_table = dynamodb.Table(os.environ['user_table'])

    data = json.loads(event['body'])

    # print("headers", headers)
    print("data", data)

    if 'auth_token' not in data:
        raise Exception("Unauthorized Access.")

    token = data['auth_token']

    type = data['type']
    print("type", type)
    desc = data['desc']
    print("desc", desc)

    if not type or not desc:
        print("In if")
        logging.error("type or description empty. ")
        raise Exception("Couldn't create the todo item.")

    timestamp = int(time.time() * 1000)

    result = user_table.get_item(
        Key={
            'user_id': str(token)
        }
    )
    print("result", result)

    if result['Item'] == None:
        raise Exception("Unauthorized Access.")

    user = result['Item']

    print("user", user)

    item = {
        "event_id": str(uuid.uuid1()),
        "event_type": type,
        "event_desc": desc,
        "created_at": timestamp,
        "user": json.dumps(user, cls=decimalencoder.DecimalEncoder)
    }
    print("item", item)

    event_table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "event_id": str(item['event_id']),
            "type": str(type)
        })
    }

    return response


def delete(event, context):
    event_table = dynamodb.Table(os.environ['event_table'])

    event_table.delete_item(
        Key={
            'event_id': event['pathParameters']['id']
        }
    )

    response = {
        "statusCode": 200
    }
    return response


def update(event, context):
    event_table = dynamodb.Table(os.environ['event_table'])
    user_table = dynamodb.Table(os.environ['user_table'])

    data = json.loads(event['body'])

    # print("headers", headers)
    print("data", data)

    if 'auth_token' not in data:
        raise Exception("Unauthorized Access.")

    token = data['auth_token']

    type = data['type']
    print("type", type)
    desc = data['desc']
    print("desc", desc)

    result = user_table.get_item(
        Key={
            'user_id': str(token)
        }
    )
    print("result", result)

    timestamp = int(time.time() * 1000)

    if result['Item'] == None:
        raise Exception("Unauthorized Access.")

    user = result['Item']

    result = event_table.update_item(
        Key={
            'event_id': event['pathParameters']['id']
        },
        ExpressionAttributeValues={
            ':d': data['desc'],
            ':t': data['type']
            },
        UpdateExpression="set event_type = :t, event_desc = :d",

        ReturnValues='ALL_NEW',
    )

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(result['Attributes'],
                           cls=decimalencoder.DecimalEncoder)
    }

    return response


