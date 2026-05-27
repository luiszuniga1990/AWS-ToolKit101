import json
import boto3


def handler(event, context):
    """Analiza Logging & Monitoring: CloudTrail, Config, CloudWatch."""
    body = json.loads(event.get('body', '{}'))
    access_key = body.get('access_key')
    secret_key = body.get('secret_key')
    region = body.get('region', 'us-east-1')

    findings = []

    # Check 1: CloudTrail habilitado
    ct = boto3.client('cloudtrail', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key, region_name=region)
    try:
        trails = ct.describe_trails()['trailList']
        if not trails:
            findings.append({
                'category': 'logging',
                'severity': 'CRITICAL',
                'check': 'CloudTrail no está habilitado',
                'resource': 'cloudtrail',
                'recommendation': 'Habilitar CloudTrail en todas las regiones',
                'maturity_phase': 'QUICK_WINS',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
            })
        else:
            for trail in trails:
                if not trail.get('IsMultiRegionTrail'):
                    findings.append({
                        'category': 'logging',
                        'severity': 'HIGH',
                        'check': 'CloudTrail no es multi-región',
                        'resource': trail['Name'],
                        'recommendation': 'Configurar CloudTrail como multi-región',
                        'maturity_phase': 'FOUNDATIONAL',
                        'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
                    })
                if not trail.get('LogFileValidationEnabled'):
                    findings.append({
                        'category': 'logging',
                        'severity': 'MEDIUM',
                        'check': 'Log file validation deshabilitado',
                        'resource': trail['Name'],
                        'recommendation': 'Habilitar validación de integridad de logs',
                        'maturity_phase': 'FOUNDATIONAL',
                        'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
                    })
    except Exception as e:
        findings.append({
            'category': 'logging',
            'severity': 'INFO',
            'check': f'Error consultando CloudTrail: {str(e)}',
            'resource': 'cloudtrail',
            'recommendation': 'Verificar permisos de lectura para CloudTrail',
            'maturity_phase': 'QUICK_WINS',
            'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
        })

    # Check 2: AWS Config habilitado
    config = boto3.client('config', aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key, region_name=region)
    try:
        recorders = config.describe_configuration_recorders()['ConfigurationRecorders']
        if not recorders:
            findings.append({
                'category': 'logging',
                'severity': 'HIGH',
                'check': 'AWS Config no está habilitado',
                'resource': 'config',
                'recommendation': 'Habilitar AWS Config para registro de cambios',
                'maturity_phase': 'FOUNDATIONAL',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
            })
    except Exception:
        pass

    # Check 3: CloudWatch alarms básicas
    cw = boto3.client('cloudwatch', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key, region_name=region)
    try:
        alarms = cw.describe_alarms()['MetricAlarms']
        if not alarms:
            findings.append({
                'category': 'logging',
                'severity': 'MEDIUM',
                'check': 'No hay alarmas de CloudWatch configuradas',
                'resource': 'cloudwatch',
                'recommendation': 'Configurar alarmas para eventos de seguridad críticos',
                'maturity_phase': 'FOUNDATIONAL',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
            })
    except Exception:
        pass

    return response(200, {
        'sector': 'Logging & Monitoring',
        'total_findings': len(findings),
        'findings': findings
    })


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body, default=str)
    }
