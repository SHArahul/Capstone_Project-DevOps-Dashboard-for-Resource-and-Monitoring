from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from fetcher.fetch_aws_cost import *
from fetcher.azure_cost_fetch import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to the Cloud Cost API. Use /aws-cost for AWS cost summary and /azure-cost for Azure cost summary.'
    }), 200
@app.route('/aws-cost', methods=['GET'])
def cost_summary():
    # Determine the time period for the cost summary
    start_date = get_last_update_date(database,create_aws_table_query, "aws_costs")
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

    try:
        result = get_aws_cost_summary(time_period, metrics, groupBy)
        # return jsonify(result)
        # Store the result in PostgreSQL
        store_cost_data(result, create_aws_table_query, "aws_costs")
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return json.dumps({'status': 'error', 'message': f"Expired Access Token: {str(e)}"}), 500   

@app.route('/azure-cost', methods=['GET'])
def azure_cost_summary():
    start_date = get_last_update_date(azure_db_name,create_azure_table_query, "azure_costs")
    end_date = datetime.now(timezone.utc)
    if start_date:
        next_start_date = start_date + timedelta(days=1)
        start_date = next_start_date.strftime('%Y-%m-%dT00:00:00Z')
    else:
        start_date = end_date - timedelta(days=7)

    granularity="Daily"
    
    try:
        result = fetch_azure_cost_summary(start_date, end_date, granularity)

        store_cost_data(result, create_azure_table_query, "azure_costs")
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return json.dumps({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
