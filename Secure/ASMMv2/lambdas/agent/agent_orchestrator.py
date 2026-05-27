import json
import boto3
import os

MODEL_ID = os.environ.get('MODEL_ID', 'amazon.nova-pro-v1:0')

MATURITY_PHASES = {
    'QUICK_WINS': {
        'level': 1,
        'name': 'Quick Wins',
        'description': 'Acciones inmediatas de seguridad básica',
        'url': 'https://maturitymodel.security.aws.dev/en/model/'
    },
    'FOUNDATIONAL': {
        'level': 2,
        'name': 'Foundational',
        'description': 'Fundamentos de seguridad establecidos',
        'url': 'https://maturitymodel.security.aws.dev/en/model/'
    },
    'EFFICIENT': {
        'level': 3,
        'name': 'Efficient',
        'description': 'Seguridad eficiente y automatizada',
        'url': 'https://maturitymodel.security.aws.dev/en/model/'
    },
    'OPTIMIZED': {
        'level': 4,
        'name': 'Optimized',
        'description': 'Seguridad optimizada y proactiva',
        'url': 'https://maturitymodel.security.aws.dev/en/model/'
    }
}


def handler(event, context):
    """Orquesta el agente: recibe findings y genera recomendaciones con IA."""
    body = json.loads(event.get('body', '{}'))
    assessment_results = body.get('assessment_results', [])
    user_question = body.get('question', '')

    # Consolidar findings
    all_findings = []
    for result in assessment_results:
        all_findings.extend(result.get('findings', []))

    # Determinar fase de madurez actual
    current_phase = determine_maturity_phase(all_findings)

    # Construir prompt para el modelo
    prompt = build_prompt(all_findings, current_phase, user_question)

    # Invocar Bedrock
    bedrock = boto3.client('bedrock-runtime')
    response_body = invoke_model(bedrock, prompt)

    return response(200, {
        'current_phase': current_phase,
        'phase_info': MATURITY_PHASES.get(current_phase, {}),
        'total_findings': len(all_findings),
        'critical_count': len([f for f in all_findings if f.get('severity') == 'CRITICAL']),
        'high_count': len([f for f in all_findings if f.get('severity') == 'HIGH']),
        'agent_response': response_body,
        'findings_summary': all_findings
    })


def determine_maturity_phase(findings):
    """Determina la fase de madurez basada en los findings."""
    critical = [f for f in findings if f.get('severity') == 'CRITICAL']
    high = [f for f in findings if f.get('severity') == 'HIGH']
    quick_wins = [f for f in findings if f.get('maturity_phase') == 'QUICK_WINS']

    if critical or quick_wins:
        return 'QUICK_WINS'
    elif high:
        return 'FOUNDATIONAL'
    elif findings:
        return 'EFFICIENT'
    else:
        return 'OPTIMIZED'


def build_prompt(findings, phase, user_question):
    """Construye el prompt para el modelo de IA."""
    findings_text = json.dumps(findings, indent=2, ensure_ascii=False)
    phase_info = MATURITY_PHASES[phase]

    prompt = f"""Eres un experto en seguridad AWS. Analiza los siguientes hallazgos de seguridad 
basándote en el AWS Security Maturity Model v2 (https://maturitymodel.security.aws.dev/en/model/).

FASE ACTUAL DE MADUREZ: {phase_info['name']} (Nivel {phase_info['level']})
Descripción: {phase_info['description']}

HALLAZGOS:
{findings_text}

Responde en español. Incluye:
1. Resumen de la fase de madurez actual
2. Las recomendaciones CRÍTICAS que se deben atender primero
3. Para cada recomendación, incluye el link al cuadro respectivo del AWS Security Maturity Model v2
4. Pasos concretos para avanzar a la siguiente fase

{f'PREGUNTA DEL USUARIO: {user_question}' if user_question else ''}
"""
    return prompt


def invoke_model(bedrock, prompt):
    """Invoca el modelo de Bedrock (Amazon Nova Pro)."""
    try:
        resp = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'inferenceConfig': {'max_new_tokens': 4096},
                'messages': [{'role': 'user', 'content': [{'text': prompt}]}]
            })
        )
        result = json.loads(resp['body'].read())
        return result['output']['message']['content'][0]['text']
    except Exception as e:
        return f'Error invocando modelo: {str(e)}'


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body, default=str, ensure_ascii=False)
    }
