from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

load_dotenv()


# Function to get AWS Cost Explorer summary

def get_aws_cost_summary(time_period, metrics, group_by, region='ca-central-1',granularity='DAILY'):
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
    

# Function to store AWS Cost Explorer summary to PostgreSQL port 5432 (simulated here as a JSON file)
def store_aws_cost_data(json_data):

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    # --- Helper: Ensure database exists ---
    def ensure_database_exists():
        conn = psycopg2.connect(host=host, user=user, password=password, dbname="postgres")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{database}"')
            print(f"✅ Database '{database}' created.")
        else:
            print(f"ℹ️ Database '{database}' already exists.")
        cur.close()
        conn.close()

    # --- Helper: Ensure table exists ---
    def ensure_table_exists(conn):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS aws_costs (
            id SERIAL PRIMARY KEY,
            service_name TEXT,
            amortized_cost NUMERIC,
            blended_cost NUMERIC,
            unblended_cost NUMERIC,
            usage_quantity NUMERIC,
            unit TEXT
        );
        """
        cur = conn.cursor()
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
        print("✅ Table 'aws_costs' ready.")

    # --- Helper: Insert data ---
    def insert_cost_data(conn, data):
        cur = conn.cursor()
        for entry in data:
            for group in entry.get("Groups", []):
                service_name = group["Keys"][0]
                metrics = group["Metrics"]

                amortized_cost = float(metrics["AmortizedCost"]["Amount"])
                blended_cost = float(metrics["BlendedCost"]["Amount"])
                unblended_cost = float(metrics["UnblendedCost"]["Amount"])
                usage_quantity = float(metrics["UsageQuantity"]["Amount"])
                unit = metrics["UsageQuantity"]["Unit"]

                cur.execute("""
                    INSERT INTO aws_costs (
                        service_name, amortized_cost, blended_cost, unblended_cost, usage_quantity, unit
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (service_name, amortized_cost, blended_cost, unblended_cost, usage_quantity, unit))
        conn.commit()
        cur.close()
        print("✅ Data inserted successfully!")

    # --- Main process ---
    ensure_database_exists()

    conn = psycopg2.connect(host=host, user=user, password=password, dbname=database)
    ensure_table_exists(conn)
    insert_cost_data(conn, json_data)
    conn.close()

    print("🎉 AWS cost data stored successfully.")


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
    # Store the result in PostgreSQL
    try:
        store_aws_cost_data(result)
        return json.dumps({
            'status': 'success',
            'data': result
        }), 200   
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)






