import json
import boto3

# Políticas permitidas (solo lectura)
ALLOWED_POLICIES = [
    'arn:aws:iam::aws:policy/ReadOnlyAccess',
    'arn:aws:iam::aws:policy/SecurityAudit',
    'arn:aws:iam::aws:policy/ViewOnlyAccess'
]

# Acciones de escritura que NO deben estar presentes
WRITE_ACTIONS_PREFIXES = [
    'Create', 'Delete', 'Put', 'Update', 'Modify',
    'Attach', 'Detach', 'Add', 'Remove', 'Terminate',
    'Run', 'Start', 'Stop', 'Reboot'
]


def handler(event, context):
    """Verifica que las credenciales solo tienen políticas de lectura."""
    body = json.loads(event.get('body', '{}'))
    access_key = body.get('access_key')
    secret_key = body.get('secret_key')

    if not access_key or not secret_key:
        return response(400, {'error': 'access_key y secret_key son requeridos'})

    try:
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        sts = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        # Obtener info del usuario
        identity = sts.get_caller_identity()
        arn = identity['Arn']
        username = arn.split('/')[-1]

        # Obtener políticas attached al usuario
        attached = iam.list_attached_user_policies(UserName=username)
        attached_arns = [p['PolicyArn'] for p in attached['AttachedPolicies']]

        # Verificar que solo tiene políticas de lectura
        unauthorized_policies = [p for p in attached_arns if p not in ALLOWED_POLICIES]

        # Verificar inline policies
        inline = iam.list_user_policies(UserName=username)
        has_inline = len(inline['PolicyNames']) > 0

        # Verificar grupos del usuario
        groups = iam.list_groups_for_user(UserName=username)
        group_issues = []
        for group in groups['Groups']:
            group_policies = iam.list_attached_group_policies(GroupName=group['GroupName'])
            for p in group_policies['AttachedPolicies']:
                if p['PolicyArn'] not in ALLOWED_POLICIES:
                    group_issues.append(p['PolicyArn'])

        is_readonly = (
            len(unauthorized_policies) == 0
            and not has_inline
            and len(group_issues) == 0
        )

        return response(200, {
            'is_readonly': is_readonly,
            'username': username,
            'attached_policies': attached_arns,
            'unauthorized_policies': unauthorized_policies + group_issues,
            'has_inline_policies': has_inline,
            'message': 'Credenciales válidas - solo lectura' if is_readonly
                       else 'BLOQUEADO: se detectaron permisos más allá de lectura'
        })

    except Exception as e:
        return response(500, {'error': str(e)})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
