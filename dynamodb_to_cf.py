import re

import boto3
import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--on-demand",
    action="store_true",
    help="Use on-demand billing mode for the tables",
)
parser.add_argument(
    "--region",
    nargs="?",
    const=1,
    type=str,
    default="us-east-1",
    help="AWS region to use (default: us-east-1)",
)
parser.add_argument(
    "--profile",
    nargs="?",
    const=1,
    type=str,
    default="default",
    help="AWS profile to use (default: default)",
)

args = parser.parse_args()

boto3.setup_default_session(profile_name=args.profile)

dynamodb = boto3.client("dynamodb", region_name=args.region)
tables = dynamodb.list_tables()["TableNames"]


def sanitize_name(name):
    splited = re.split(r"[\-\_\.]+", name)
    capitalized = "".join(i.capitalize() for i in splited)
    sanitezed_name = re.sub(r"[^a-zA-Z0-9]", "", capitalized)

    return sanitezed_name


resources = {}
for table_name in tables:
    table = dynamodb.describe_table(TableName=table_name)["Table"]

    properties = {
        "TableName": table_name,
        "AttributeDefinitions": [
            {
                "AttributeName": attr["AttributeName"],
                "AttributeType": attr["AttributeType"],
            }
            for attr in table["AttributeDefinitions"]
        ],
        "KeySchema": [
            {"AttributeName": key["AttributeName"], "KeyType": key["KeyType"]}
            for key in table["KeySchema"]
        ],
    }
    if args.on_demand:
        properties["BillingMode"] = "PAY_PER_REQUEST"
    else:
        properties["ProvisionedThroughput"] = {
            "ReadCapacityUnits": table["ProvisionedThroughput"]["ReadCapacityUnits"],
            "WriteCapacityUnits": table["ProvisionedThroughput"]["WriteCapacityUnits"],
        }

    if "GlobalSecondaryIndexes" in table:
        global_secondary_indexes = []
        for index in table["GlobalSecondaryIndexes"]:
            global_secondary_indexes.append(
                {
                    "IndexName": index["IndexName"],
                    "KeySchema": [
                        {
                            "AttributeName": key["AttributeName"],
                            "KeyType": key["KeyType"],
                        }
                        for key in index["KeySchema"]
                    ],
                    "Projection": {
                        "ProjectionType": index["Projection"]["ProjectionType"]
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": index["ProvisionedThroughput"][
                            "ReadCapacityUnits"
                        ],
                        "WriteCapacityUnits": index["ProvisionedThroughput"][
                            "WriteCapacityUnits"
                        ],
                    },
                }
            )
        properties["GlobalSecondaryIndexes"] = global_secondary_indexes

    resource = {"Type": "AWS::DynamoDB::Table", "Properties": properties}
    resources[sanitize_name(table_name)] = resource

template = {"Resources": resources}

with open("template.yaml", "w") as f:
    yaml.dump(template, f)
