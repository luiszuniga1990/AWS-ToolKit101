import json
import boto3


def handler(event, context):
    """Analiza IAM: usuarios, roles, MFA, access keys, políticas."""
    body = json.loads(event.get('body', '{}'))
    access_key = body.get('access_key')
    secret_key = body.get('secret_key')

    iam = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    findings = []

    # Check 1: MFA habilitado para todos los usuarios
    users = iam.list_users()['Users']
    for user in users:
        mfa = iam.list_mfa_devices(UserName=user['UserName'])
        if not mfa['MFADevices']:
            findings.append({
                'category': 'identity',
                'severity': 'CRITICAL',
                'check': 'MFA no habilitado',
                'resource': user['UserName'],
                'recommendation': 'Habilitar MFA para todos los usuarios IAM',
                'maturity_phase': 'QUICK_WINS',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/identity/'
            })

    # Check 2: Access keys rotadas (>90 días)
    for user in users:
        keys = iam.list_access_keys(UserName=user['UserName'])
        for key in keys['AccessKeyMetadata']:
            if key['Status'] == 'Active':
                from datetime import datetime, timezone
                age = (datetime.now(timezone.utc) - key['CreateDate']).days
                if age > 90:
                    findings.append({
                        'category': 'identity',
                        'severity': 'HIGH',
                        'check': 'Access key sin rotar',
                        'resource': f"{user['UserName']} - {key['AccessKeyId']}",
                        'detail': f'{age} días sin rotar',
                        'recommendation': 'Rotar access keys cada 90 días',
                        'maturity_phase': 'QUICK_WINS',
                        'reference': 'https://maturitymodel.security.aws.dev/en/model/identity/'
                    })

    # Check 3: Root account access keys
    try:
        summary = iam.get_account_summary()['SummaryMap']
        if summary.get('AccountAccessKeysPresent', 0) > 0:
            findings.append({
                'category': 'identity',
                'severity': 'CRITICAL',
                'check': 'Root account tiene access keys',
                'resource': 'root',
                'recommendation': 'Eliminar access keys del root account',
                'maturity_phase': 'QUICK_WINS',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/identity/'
            })
        if summary.get('AccountMFAEnabled', 0) == 0:
            findings.append({
                'category': 'identity',
                'severity': 'CRITICAL',
                'check': 'Root account sin MFA',
                'resource': 'root',
                'recommendation': 'Habilitar MFA en root account',
                'maturity_phase': 'QUICK_WINS',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/identity/'
            })
    except Exception:
        pass

    # Check 4: Password policy
    try:
        policy = iam.get_account_password_policy()['PasswordPolicy']
        if not policy.get('RequireLowercaseCharacters'):
            findings.append({
                'category': 'identity',
                'severity': 'MEDIUM',
                'check': 'Password policy débil',
                'resource': 'account-password-policy',
                'recommendation': 'Configurar password policy con complejidad requerida',
                'maturity_phase': 'FOUNDATIONAL',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/identity/'
            })
    except iam.exceptions.NoSuchEntityException:
        findings.append({
            'category': 'identity',
            'severity': 'HIGH',
            'check': 'No existe password policy',
            'resource': 'account-password-policy',
            'recommendation': 'Crear password policy para la cuenta',
            'maturity_phase': 'QUICK_WINS',
            'reference': 'https://maturitymodel.security.aws.dev/en/model/identity/'
        })

    return response(200, {
        'sector': 'IAM & Identity',
        'total_findings': len(findings),
        'findings': findings
    })


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body, default=str)
    }
