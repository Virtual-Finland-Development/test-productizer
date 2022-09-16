# @see: https://www.pulumi.com/blog/lambda-urls-launch/
import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_native as aws_native
from pulumi_command import local

lambda_role = aws_native.iam.Role(
    "lambda_role",
    assume_role_policy_document=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                    "Effect": "Allow",
                    "Sid": "",
                },
            ],
        }
    ),
)

lambda_role_attachment = aws.iam.RolePolicyAttachment(
    "lambda_role_attachment",
    role=pulumi.Output.concat(lambda_role.role_name),  # type: ignore
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

productizerer_function = aws.lambda_.Function(
    "test",
    runtime="python3.9",
    role=lambda_role.arn,
    handler="productizer.main.handler",
    code=pulumi.AssetArchive(
        {
            ".": pulumi.FileArchive("."),
        }
    ),
)

lambda_url = aws_native.lambda_.Url(
    "test",
    target_function_arn=productizerer_function.arn,
    auth_type=aws_native.lambda_.UrlAuthType.NONE,
)

add_permissions = local.Command(
    "add_permissions",
    create=pulumi.Output.concat(
        "aws lambda add-permission --profile virtualfinland --function-name ",
        productizerer_function.name,
        " --action lambda:InvokeFunctionUrl --principal '*' --function-url-auth-type NONE --statement-id FunctionURLAllowPublicAccess",
    ),
    opts=pulumi.ResourceOptions(delete_before_replace=True),
)

pulumi.export("url", lambda_url.function_url)
