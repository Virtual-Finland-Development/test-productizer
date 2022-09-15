import pulumi
import json

from pulumi_aws_native import lambda_, stepfunctions, iam, config
from productizer.utils.settings import get_setting

lambda_role = iam.Role(
    "lambdaRole",
    assume_role_policy_document=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Effect": "Allow",
                    "Sid": "",
                }
            ],
        }
    ),
    policies=[
        iam.RolePolicyArgs(
            policy_name="lambdaRolePolicy",
            policy_document=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "arn:aws:logs:*:*:*",
                        }
                    ],
                }
            ),
        )
    ],
)

sfn_role = iam.Role(
    "sfnRole",
    assume_role_policy_document=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": f"states.{config.region}.amazonaws.com"},  # type: ignore
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    policies=[
        iam.RolePolicyArgs(
            policy_name="sfnRolePolicy",
            policy_document=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["lambda:InvokeFunction"],
                            "Resource": "*",
                        }
                    ],
                }
            ),
        )
    ],
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

state_defn = state_machine = stepfunctions.StateMachine(
    "stateMachine",
    role_arn=sfn_role.arn,
    definition_string=json.dumps(
        {
            "Comment": "Productizerer deployment state machine",
            "StartAt": "Productizerer",
            "States": {
                "Productizerer": {
                    "Type": "Task",
                    "Resource": productizerer_fn.arn,
                    "End": True,
                }
            },
        }
    ),
)

pulumi.export("state_machine_arn", state_machine.id)
