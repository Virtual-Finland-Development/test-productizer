import pulumi
from pulumi_aws_native import lambda_, stepfunctions, config, iam
from productizer.utils.settings import get_setting

lambda_role = iam.Role(
    "lambdaRole",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }""",
)  # type: ignore

lambda_role_policy = iam.RolePolicy(  # type: ignore
    "lambdaRolePolicy",
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }]
    }""",
)

sfn_role = iam.Role(
    "sfnRole",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "states.%s.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }"""
    % config.region,  # type: ignore
)

sfn_role_policy = iam.RolePolicy(  # type: ignore
    "sfnRolePolicy",
    role=sfn_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": "*"
            }
        ]
    }""",
)


productizerer_fn = lambda_.Function(
    "productizerer",
    role=lambda_role.arn,
    runtime="python3.9",
    handler="productizer.main.handler",
    environment=lambda_.FunctionEnvironmentArgs(
        variables={
            "AUTHORIZATION_GW_ENDPOINT_URL": get_setting(
                "AUTHORIZATION_GW_ENDPOINT_URL"
            )
        }
    ),
    code=pulumi.AssetArchive({".": pulumi.FileArchive("../productizer")}),  # type: ignore
)


def getStateMachineDefinition(arn: str) -> str:
    return (
        """{ 
        "Comment": "Productizerer deployment state machine",
        "StartAt": "Productizerer",
        "States": {
            "Productizerer": {
                "Type": "Task",
                "Resource": "%s",
                "End": true
            }
        }
    }"""
        % arn
    )


state_defn = state_machine = stepfunctions.StateMachine(
    "stateMachine",
    role_arn=sfn_role.arn,
    definition=productizerer_fn.arn.apply(lambda arn: getStateMachineDefinition(arn)),  # type: ignore
)

pulumi.export("state_machine_arn", state_machine.id)
