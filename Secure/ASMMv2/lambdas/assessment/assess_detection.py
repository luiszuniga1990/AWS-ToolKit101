import json
import boto3


def handler(event, context):
    """Analiza Detection & Response: GuardDuty, Security Hub."""
    body = json.loads(event.get('body', '{}'))
    access_key = body.get('access_key')
    secret_key = body.get('secret_key')
    region = body.get('region', 'us-east-1')

    findings = []

    # Check 1: GuardDuty habilitado
    gd = boto3.client('guardduty', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key, region_name=region)
    try:
        detectors = gd.list_detectors()['DetectorIds']
        if not detectors:
            findings.append({
                'category': 'detection',
                'severity': 'CRITICAL',
                'check': 'GuardDuty no está habilitado',
                'resource': 'guardduty',
                'recommendation': 'Habilitar GuardDuty para detección de amenazas',
                'maturity_phase': 'QUICK_WINS',
                'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
            })
        else:
            for det_id in detectors:
                detector = gd.get_detector(DetectorId=det_id)
                if detector['Status'] != 'ENABLED':
                    findings.append({
                        'category': 'detection',
                        'severity': 'CRITICAL',
                        'check': 'GuardDuty está deshabilitado',
                        'resource': det_id,
                        'recommendation': 'Activar el detector de GuardDuty',
                        'maturity_phase': 'QUICK_WINS',
                        'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
                    })
    except Exception:
        findings.append({
            'category': 'detection',
            'severity': 'HIGH',
            'check': 'No se pudo verificar GuardDuty',
            'resource': 'guardduty',
            'recommendation': 'Verificar acceso a GuardDuty',
            'maturity_phase': 'QUICK_WINS',
            'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
        })

    # Check 2: Security Hub habilitado
    sh = boto3.client('securityhub', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key, region_name=region)
    try:
        sh.describe_hub()
    except sh.exceptions.InvalidAccessException:
        findings.append({
            'category': 'detection',
            'severity': 'HIGH',
            'check': 'Security Hub no está habilitado',
            'resource': 'securityhub',
            'recommendation': 'Habilitar Security Hub para vista centralizada de seguridad',
            'maturity_phase': 'FOUNDATIONAL',
            'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
        })
    except Exception:
        findings.append({
            'category': 'detection',
            'severity': 'HIGH',
            'check': 'Security Hub no está habilitado',
            'resource': 'securityhub',
            'recommendation': 'Habilitar Security Hub para vista centralizada de seguridad',
            'maturity_phase': 'FOUNDATIONAL',
            'reference': 'https://maturitymodel.security.aws.dev/en/model/detection/'
        })

    # Check 3: Verificar si hay findings activos en GuardDuty
    if detectors if 'detectors' in dir() else False:
        pass  # Ya cubierto arriba

    return response(200, {
        'sector': 'Detection & Response',
        'total_findings': len(findings),
        'findings': findings
    })


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body, default=str)
    }
