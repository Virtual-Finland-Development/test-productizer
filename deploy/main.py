import json
import pulumi
from pulumi_aws import lambda_, sfn as stepfunctions, iam, config
from productizer.utils.settings import get_setting

lambda_role = iam.Role(
    "lambdaRole",
    assume_role_policy=json.dumps(
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
    inline_policies=[
        iam.RoleInlinePolicyArgs(
            name="lambdaRolePolicy",
            policy=json.dumps(
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
    assume_role_policy=json.dumps(
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
    inline_policies=[
        iam.RoleInlinePolicyArgs(
            name="sfnRolePolicy",
            policy=json.dumps(
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
    environment=lambda_.FunctionEnvironmentArgs(
        variables={
            "AUTHORIZATION_GW_ENDPOINT_URL": get_setting(
                "AUTHORIZATION_GW_ENDPOINT_URL"
            )
        }
    ),
    code=pulumi.AssetArchive({".": pulumi.FileArchive("../productizer")}),
    handler="productizer.main.handler",
)

state_defn = state_machine = stepfunctions.StateMachine(
    "stateMachine",
    role_arn=sfn_role.arn,
    definition=json.dumps(
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
