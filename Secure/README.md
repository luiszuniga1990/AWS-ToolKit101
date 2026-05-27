# Secure

Módulo de seguridad del repositorio AWS-ToolKit101. Contiene herramientas, templates y agentes para evaluar y mejorar la postura de seguridad en cuentas AWS.

## Proyectos

| Proyecto | Descripción | Estado |
|---|---|---|
| [ASMMv2](./ASMMv2/) | Agente IA que evalúa seguridad AWS contra el Security Maturity Model v2 | ✅ Activo |

## ASMMv2 — AWS Security Maturity Model v2 Agent

Agente serverless con interfaz web interactiva que analiza la seguridad de una cuenta AWS y genera recomendaciones basadas en el [AWS Security Maturity Model v2](https://maturitymodel.security.aws.dev/en/model/).

**Stack tecnológico**: Cognito · Lambda · API Gateway · Bedrock AgentCore · S3 · CloudFront

**Características**:
- Autenticación con Cognito
- Validación de credenciales read-only (bloquea si tiene permisos de escritura)
- Assessment automatizado: IAM, Logging, Detection
- Chat interactivo con recomendaciones por fase de madurez
- 5 stacks CloudFormation, 100% serverless

→ [Ver documentación completa](./ASMMv2/README.md)
