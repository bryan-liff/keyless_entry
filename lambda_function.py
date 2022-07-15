# This function expects a DynamoDB table with the following columns (NAME: TYPE):
#
# REQUIRED
# code: string
#
# OPTIONAL
# allowed_from: date (yyyy-mm-dd)
# allowed_to: date (yyyy-mm-dd)
# total_allowed: integer

import boto3
import datetime
import http.client

DYNAMO_TABLE_NAME='DYNAMO_TABLE_NAME'
BUILDING_URL = 'BUILDING_URL' # [subdomain.]domain.com OR IP Address
BUILDING_PORT = PORT
AUTH_CODE = 'YOUR_SECRET_HEADER_KEY' #Some arbitrary length, cryptologically difficut string

def lambda_handler(event, context):
    try:
        code = event['queryStringParameters']['code']
        
        dynamodb_client = boto3.client('dynamodb')
        response = dynamodb_client.get_item(TableName=DYNAMO_TABLE_NAME, Key={'code': {'S': code}})
        
        if 'Item' not in response:
            status_code = 400
        else:
            item = response['Item']
            if valid_number_of_uses(item) and valid_date_range(item):
                status_code = 200
            else:
                status_code = 400
                
        if status_code == 200:
            http_client = http.client.HTTPConnection(BUILDING_URL, BUILDING_PORT, timeout=15)
            http_client.request('GET', '/', None, {'AuthCode':AUTH_CODE})
            if "total_used" in item:
                dynamodb_client.update_item(TableName=DYNAMO_TABLE_NAME, Key={'code': {'S': code}}, UpdateExpression='SET total_used = total_used + :v', ExpressionAttributeValues={":v": {"N": "1"}})
        
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500
        }

def valid_number_of_uses(item):
    if "total_allowed" in item:
        allowed = int(item['total_allowed']['N'])
        used = int(item['total_used']['N'])
        return allowed > used
    else:
        return True
    
def valid_date_range(item):
    if "allowed_from" in item and "allowed_to" in item:
        start_time = datetime.datetime.strptime(item['allowed_from']['S'] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(item['allowed_to']['S'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        return start_time < now and now < end_time
    elif "allowed_to" in item:
        end_time = datetime.datetime.strptime(item['allowed_to']['S'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        return now < end_time
    elif "allowed_from" in item:
        start_time = datetime.datetime.strptime(item['allowed_from']['S'] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        return start_time < now
    else:
        return True