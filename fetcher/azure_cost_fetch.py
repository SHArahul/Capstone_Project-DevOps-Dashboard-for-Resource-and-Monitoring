import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping
from datetime import datetime, timedelta, timezone
import json
from fetcher.database import *

# Load environment variables
load_dotenv()

def fetch_azure_cost_summary(start_date, end_date, granularity='Daily'):

    try:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

        credential = ClientSecretCredential(
            tenant_id= os.getenv("AZURE_TENANT_ID"),  # type: ignore
            client_id=os.getenv("AZURE_CLIENT_ID"), # type: ignore
            client_secret=os.getenv("AZURE_CLIENT_SECRET")   # type: ignore
        )

        client = CostManagementClient(credential)
        scope = f"/subscriptions/{subscription_id}"
        query = QueryDefinition(
            type="Usage",
            timeframe="Custom",
            time_period=QueryTimePeriod(
                from_property=start_date,
                to=end_date
            ),
            dataset=QueryDataset(
                granularity=granularity,
                aggregation={
                    "cost": QueryAggregation(
                        name="PreTaxCost",
                        function="Sum"
                    )
                },
                grouping=[
                    QueryGrouping(type="Dimension", name="ServiceName"),
                    QueryGrouping(type="Dimension", name="ResourceLocation"),
                ]
            )
        )
        
        result = client.query.usage(scope=scope, parameters=query)
        if result is not None and hasattr(result, "rows") and result.rows is not None:
            return json.loads(json.dumps(result.rows, indent=1, default=str))
        else:
            print("No cost data returned from Azure Cost Management API.")
    except Exception as e:
        print(f"An error occurred while fetching Azure cost data: {e}")
        return json.dumps({'status': 'error', 'message': str(e)}), 500

# print(f"Cost data from {start_date} to {end_date}: {result}")

