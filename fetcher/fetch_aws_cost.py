
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
import json
from fetcher.database import *

# Load environment variables
load_dotenv()

# Function to get AWS Cost Explorer summary

def get_aws_cost_summary(time_period, metrics, group_by, region=None,granularity='DAILY'):
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key =  os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", region)    
    try:
        if aws_access_key and aws_secret_key:
            client = boto3.client('ce',
                                  aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=aws_secret_key,
                                  region_name=aws_region
                                  )
        else:
            client = boto3.client('ce')

        response = client.get_cost_and_usage(
            TimePeriod=time_period,
            Granularity=granularity,
            Metrics=metrics,
            GroupBy=group_by
        )

        return json.loads(json.dumps(response['ResultsByTime'], indent=1, default=str))
        # return json.loads(json.dumps(response['ResultsByTime'], indent=50, default=str))  # For pretty printing with indentation

    except NoCredentialsError:
        print("AWS credentials not found.")
        return json.dumps({'status': 'error', 'message': 'AWS credentials not found'}), 401
    except PartialCredentialsError:
        print("Incomplete AWS credentials.")
        return json.dumps({'status': 'error', 'message': 'Incomplete AWS credentials'}), 401
    except Exception as e:
        print(f"An error occurred: {e}")
        return json.dumps({'status': 'error', 'message': str(e)}), 500







