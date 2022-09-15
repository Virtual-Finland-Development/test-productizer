# @see: https://www.pulumi.com/blog/lambda-urls-launch/
import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_native as aws_native

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

productizerer_function = aws_native.lambda_.Function(
    "test",
    runtime="nodejs16.x",
    role=lambda_role.arn,
    handler="index.handler",
    code=aws_native.lambda_.FunctionCodeArgs(
        zip_file="exports.handler = function(event, context, callback){ callback(null, {'response': 'productizerer'}); };",
    ),
)

lambda_url = aws_native.lambda_.Url(
    "test",
    target_function_arn=productizerer_function.arn,
    auth_type=aws_native.lambda_.UrlAuthType.NONE,
)

pulumi.export("url", lambda_url.function_url)
