from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

# Function to get AWS Cost Explorer summary

def get_aws_cost_summary(time_period, metrics, group_by, region='ca-central-1',granularity='DAILY'):
    try:
        client = boto3.client('ce')

        response = client.get_cost_and_usage(
            TimePeriod=time_period,
            Granularity=granularity,
            Metrics=metrics,
            GroupBy=group_by
        )

        return json.loads(json.dumps(response, indent=1, default=str))
        # return json.loads(json.dumps(response, indent=10, default=str))  # For pretty printing with indentation

    except NoCredentialsError:
        print("AWS credentials not found.")
        return json.dumps({'status': 'error', 'message': 'AWS credentials not found'}), 401
    except PartialCredentialsError:
        print("Incomplete AWS credentials.")
        return json.dumps({'status': 'error', 'message': 'Incomplete AWS credentials'}), 401
    except Exception as e:
        print(f"An error occurred: {e}")
        return json.dumps({'status': 'error', 'message': str(e)}), 500
    

# Function to store AWS Cost Explorer summary to PostgreSQL (simulated here as a JSON file)
def store_aws_cost_summary(data, filename='aws_cost_summary.json'):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully stored in {filename}")
        return True
    except Exception as e:
        print(f"Failed to store data: {e}")
        return False


@app.route('/cost-summary', methods=['GET'])
def cost_summary():

    time_period = {
        'Start': '2025-04-12',
        'End': '2025-09-28'
    }

    # Define the metrics and groupby to retrieve
    metrics = [
        "AmortizedCost",
        "BlendedCost",
        "NetAmortizedCost",
        "NetUnblendedCost",
        "NormalizedUsageAmount",
        "UnblendedCost",
        "UsageQuantity"

        ]

    groupBy = [
        {'Type': 'DIMENSION', 'Key': 'SERVICE'}, 
        # {'Type': 'DIMENSION', 'Key': 'REGION'}
        
        ]

    result = get_aws_cost_summary(time_period, metrics, groupBy)
    return result

if __name__ == '__main__':
    app.run(debug=True)






