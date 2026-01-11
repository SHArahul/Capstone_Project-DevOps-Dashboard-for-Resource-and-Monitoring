from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
import json
from datetime import datetime, timedelta

app = Flask(__name__)

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
    

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

def connect_db():
    ensure_database_exists()
    conn = psycopg2.connect(host=host, user=user, password=password, dbname=database)
    conn.autocommit = True
    return conn

# --- Helper: Ensure database exists ---
def ensure_database_exists():
    conn = psycopg2.connect(host=host, user=user, password=password, dbname='postgres')
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
        date DATE,
        region TEXT,
        service_name TEXT,
        amortized_cost NUMERIC,
        amortized_cost_unit TEXT,
        blended_cost NUMERIC,
        blended_cost_unit TEXT,
        unblended_cost NUMERIC,
        unblended_cost_unit TEXT,
        usage_quantity NUMERIC,
        usage_quantity_unit TEXT
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
            region = group["Keys"][1]
            date = entry["TimePeriod"]["Start"]
            metrics = group["Metrics"]

            amortized_cost = metrics["AmortizedCost"]["Amount"]
            blended_cost = metrics["BlendedCost"]["Amount"]
            unblended_cost = metrics["UnblendedCost"]["Amount"]
            usage_quantity = metrics["UsageQuantity"]["Amount"]
            amortized_cost_unit = metrics["AmortizedCost"]["Unit"]
            blended_cost_unit = metrics["BlendedCost"]["Unit"]
            unblended_cost_unit = metrics["UnblendedCost"]["Unit"]
            usage_quantity_unit = metrics["UsageQuantity"]["Unit"]

            cur.execute("""INSERT INTO aws_costs (date, region,service_name, amortized_cost, amortized_cost_unit, blended_cost, blended_cost_unit , unblended_cost, unblended_cost_unit, usage_quantity, usage_quantity_unit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (date, region ,service_name, amortized_cost, amortized_cost_unit, blended_cost, blended_cost_unit, unblended_cost, unblended_cost_unit, usage_quantity, usage_quantity_unit))
    conn.commit()
    cur.close()
    print("✅ Data inserted successfully!")

# Function to store AWS Cost Explorer summary to PostgreSQL port 5432 (simulated here as a JSON file)
def store_aws_cost_data(json_data):

    # --- Main process ---
    conn = connect_db()
    ensure_table_exists(conn)
    insert_cost_data(conn, json_data)
    conn.close()

    print("🎉 AWS cost data stored successfully.")

# --- Find last update date in the database ---
def get_last_update_date():
    conn = connect_db()
    ensure_table_exists(conn)
    cur = conn.cursor()
    cur.execute("SELECT MAX(date) FROM aws_costs;")
    result = cur.fetchone()
    cur.close()
    if result and result[0]:
        return result[0]
    return None



@app.route('/cost-summary', methods=['GET'])
def cost_summary():
    # Determine the time period for the cost summary
    start_date = get_last_update_date()
    if start_date:
        start_date = start_date + timedelta(days=1)
    else:
        start_date = datetime.now() - timedelta(days=7)
    time_period = {
        'Start': start_date.strftime('%Y-%m-%d'),
        'End': datetime.now().strftime('%Y-%m-%d')
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
        {'Type': 'DIMENSION', 'Key': 'REGION'}
        
        ]

    result = get_aws_cost_summary(time_period, metrics, groupBy)
    # return jsonify(result)
    # Store the result in PostgreSQL
    try:
        store_aws_cost_data(result)
        return jsonify({
            'status': 'success',
            'data': result
        }), 200   
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)






