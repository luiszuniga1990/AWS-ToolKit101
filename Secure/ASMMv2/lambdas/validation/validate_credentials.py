import json
import boto3


def handler(event, context):
    """Valida que las credenciales AWS son válidas via STS GetCallerIdentity."""
    body = json.loads(event.get('body', '{}'))
    access_key = body.get('access_key')
    secret_key = body.get('secret_key')

    if not access_key or not secret_key:
        return response(400, {'error': 'access_key y secret_key son requeridos'})

    try:
        sts = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        identity = sts.get_caller_identity()
        return response(200, {
            'valid': True,
            'account': identity['Account'],
            'arn': identity['Arn'],
            'user_id': identity['UserId']
        })
    except Exception as e:
        return response(401, {'valid': False, 'error': str(e)})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
