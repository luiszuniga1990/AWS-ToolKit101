import json
import boto3


def handler(event, context):
    """Orquesta validación completa: credenciales válidas + solo lectura."""
    body = json.loads(event.get('body', '{}'))
    access_key = body.get('access_key')
    secret_key = body.get('secret_key')

    if not access_key or not secret_key:
        return response(400, {'error': 'access_key y secret_key son requeridos'})

    # Paso 1: Validar credenciales
    try:
        sts = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        identity = sts.get_caller_identity()
    except Exception as e:
        return response(401, {
            'valid': False,
            'step': 'credentials',
            'error': f'Credenciales inválidas: {str(e)}'
        })

    # Paso 2: Validar solo lectura
    try:
        arn = identity['Arn']
        username = arn.split('/')[-1]

        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        allowed = [
            'arn:aws:iam::aws:policy/ReadOnlyAccess',
            'arn:aws:iam::aws:policy/SecurityAudit',
            'arn:aws:iam::aws:policy/ViewOnlyAccess'
        ]

        attached = iam.list_attached_user_policies(UserName=username)
        attached_arns = [p['PolicyArn'] for p in attached['AttachedPolicies']]
        unauthorized = [p for p in attached_arns if p not in allowed]

        inline = iam.list_user_policies(UserName=username)
        has_inline = len(inline['PolicyNames']) > 0

        if unauthorized or has_inline:
            return response(403, {
                'valid': True,
                'is_readonly': False,
                'step': 'readonly',
                'error': 'BLOQUEADO: las credenciales tienen permisos más allá de lectura',
                'unauthorized_policies': unauthorized,
                'has_inline_policies': has_inline
            })

        return response(200, {
            'valid': True,
            'is_readonly': True,
            'account': identity['Account'],
            'username': username,
            'message': 'Validación exitosa - credenciales válidas y solo lectura'
        })

    except Exception as e:
        return response(500, {
            'valid': True,
            'step': 'readonly_check',
            'error': f'Error verificando permisos: {str(e)}'
        })


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
