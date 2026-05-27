import yaml
import pytest
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')


class CfnLoader(yaml.SafeLoader):
    pass


# Register CloudFormation intrinsic functions
for tag in ['!Ref', '!Sub', '!GetAtt', '!Select', '!Split', '!Join', '!If',
            '!Equals', '!Not', '!And', '!Or', '!FindInMap', '!Base64',
            '!Cidr', '!ImportValue', '!GetAZs', '!Condition']:
    CfnLoader.add_constructor(tag, lambda loader, node: f'{node.tag}:{node.value}')
    CfnLoader.add_multi_constructor(tag, lambda loader, suffix, node: f'{node.tag}:{node.value}')


def load_template(stack_name):
    path = os.path.join(BASE_DIR, stack_name, f'{stack_name}.yaml')
    with open(path) as f:
        return yaml.load(f, Loader=CfnLoader)


# ============ Stack 1: Auth ============

class TestStack1Auth:
    @pytest.fixture
    def template(self):
        return load_template('stack-1-auth')

    def test_has_user_pool(self, template):
        assert 'UserPool' in template['Resources']
        assert template['Resources']['UserPool']['Type'] == 'AWS::Cognito::UserPool'

    def test_has_user_pool_client(self, template):
        assert 'UserPoolClient' in template['Resources']
        assert template['Resources']['UserPoolClient']['Type'] == 'AWS::Cognito::UserPoolClient'

    def test_has_identity_pool(self, template):
        assert 'IdentityPool' in template['Resources']
        assert template['Resources']['IdentityPool']['Type'] == 'AWS::Cognito::IdentityPool'

    def test_no_unauthenticated_access(self, template):
        props = template['Resources']['IdentityPool']['Properties']
        assert props['AllowUnauthenticatedIdentities'] is False

    def test_client_no_secret(self, template):
        props = template['Resources']['UserPoolClient']['Properties']
        assert props['GenerateSecret'] is False

    def test_exports_outputs(self, template):
        outputs = template['Outputs']
        assert 'UserPoolId' in outputs
        assert 'UserPoolClientId' in outputs
        assert 'IdentityPoolId' in outputs
        assert 'UserPoolArn' in outputs


# ============ Stack 2: Frontend ============

class TestStack2Frontend:
    @pytest.fixture
    def template(self):
        return load_template('stack-2-frontend')

    def test_has_s3_bucket(self, template):
        assert 'FrontendBucket' in template['Resources']
        assert template['Resources']['FrontendBucket']['Type'] == 'AWS::S3::Bucket'

    def test_s3_blocks_public_access(self, template):
        props = template['Resources']['FrontendBucket']['Properties']
        block = props['PublicAccessBlockConfiguration']
        assert block['BlockPublicAcls'] is True
        assert block['BlockPublicPolicy'] is True
        assert block['IgnorePublicAcls'] is True
        assert block['RestrictPublicBuckets'] is True

    def test_has_cloudfront(self, template):
        assert 'CloudFrontDistribution' in template['Resources']
        assert template['Resources']['CloudFrontDistribution']['Type'] == 'AWS::CloudFront::Distribution'

    def test_cloudfront_https_only(self, template):
        dist = template['Resources']['CloudFrontDistribution']['Properties']['DistributionConfig']
        assert dist['DefaultCacheBehavior']['ViewerProtocolPolicy'] == 'redirect-to-https'

    def test_has_oac(self, template):
        assert 'OriginAccessControl' in template['Resources']

    def test_exports_outputs(self, template):
        outputs = template['Outputs']
        assert 'FrontendBucketName' in outputs
        assert 'CloudFrontDomainName' in outputs


# ============ Stack 3: Validation ============

class TestStack3Validation:
    @pytest.fixture
    def template(self):
        return load_template('stack-3-validation')

    def test_has_api_gateway(self, template):
        assert 'ValidationApi' in template['Resources']
        assert template['Resources']['ValidationApi']['Type'] == 'AWS::ApiGatewayV2::Api'

    def test_has_three_lambdas(self, template):
        lambdas = [k for k, v in template['Resources'].items()
                   if v['Type'] == 'AWS::Serverless::Function']
        assert len(lambdas) == 3

    def test_lambda_names(self, template):
        assert 'ValidateCredentialsFunction' in template['Resources']
        assert 'ValidateReadOnlyFunction' in template['Resources']
        assert 'ValidateConnectionFunction' in template['Resources']

    def test_runtime_python312(self, template):
        assert template['Globals']['Function']['Runtime'] == 'python3.12'

    def test_has_cors(self, template):
        props = template['Resources']['ValidationApi']['Properties']
        assert 'CorsConfiguration' in props

    def test_exports_api_url(self, template):
        assert 'ValidationApiUrl' in template['Outputs']


# ============ Stack 4: Assessment ============

class TestStack4Assessment:
    @pytest.fixture
    def template(self):
        return load_template('stack-4-assessment')

    def test_has_api_gateway(self, template):
        assert 'AssessmentApi' in template['Resources']

    def test_has_three_lambdas(self, template):
        lambdas = [k for k, v in template['Resources'].items()
                   if v['Type'] == 'AWS::Serverless::Function']
        assert len(lambdas) == 3

    def test_lambda_names(self, template):
        assert 'AssessIamFunction' in template['Resources']
        assert 'AssessLoggingFunction' in template['Resources']
        assert 'AssessDetectionFunction' in template['Resources']

    def test_runtime_python312(self, template):
        assert template['Globals']['Function']['Runtime'] == 'python3.12'

    def test_timeout_sufficient(self, template):
        assert template['Globals']['Function']['Timeout'] == 120

    def test_exports_api_url(self, template):
        assert 'AssessmentApiUrl' in template['Outputs']


# ============ Stack 5: Agent ============

class TestStack5Agent:
    @pytest.fixture
    def template(self):
        return load_template('stack-5-agent')

    def test_has_kb_bucket(self, template):
        assert 'KnowledgeBaseBucket' in template['Resources']
        assert template['Resources']['KnowledgeBaseBucket']['Type'] == 'AWS::S3::Bucket'

    def test_has_agent_role(self, template):
        assert 'AgentRole' in template['Resources']
        assert template['Resources']['AgentRole']['Type'] == 'AWS::IAM::Role'

    def test_agent_role_assumes_bedrock(self, template):
        policy = template['Resources']['AgentRole']['Properties']['AssumeRolePolicyDocument']
        principals = [s['Principal']['Service'] for s in policy['Statement']]
        assert 'bedrock.amazonaws.com' in principals

    def test_has_orchestrator_lambda(self, template):
        assert 'AgentOrchestratorFunction' in template['Resources']

    def test_has_api_gateway(self, template):
        assert 'AgentApi' in template['Resources']

    def test_kb_bucket_blocks_public(self, template):
        props = template['Resources']['KnowledgeBaseBucket']['Properties']
        block = props['PublicAccessBlockConfiguration']
        assert block['BlockPublicAcls'] is True

    def test_exports_outputs(self, template):
        outputs = template['Outputs']
        assert 'AgentApiUrl' in outputs
        assert 'KnowledgeBaseBucketName' in outputs
