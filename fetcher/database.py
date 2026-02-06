# fetcher/database.py
from datetime import datetime
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql


load_dotenv()

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
azure_db_name = os.getenv("AZURE_DB_NAME")
gcp_db_name = os.getenv("GCP_DB_NAME")

# Table creation queries for AWS
create_aws_table_query = """
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
# Table creation queries for Azure
create_azure_table_query = """
    CREATE TABLE IF NOT EXISTS azure_costs (
        id SERIAL PRIMARY KEY,
        date DATE,
        region TEXT,
        service_name TEXT,
        amount NUMERIC,
        unit TEXT
    );
    """ 


def connect_db(db_name):
    # AWS Cost Explorer Database
    ensure_database_exists(db_name)
    try:     
        conn = psycopg2.connect(host=host, user=user, password=password, dbname=db_name)
        conn.autocommit = True
        return conn
    except psycopg2.DatabaseError as e:
        print(f"Error connecting to database {db_name}: {e}")
        raise

# --- Helper: Ensure database exists ---
def ensure_database_exists(database_name):
    try:
        conn = psycopg2.connect(host=host, user=user, password=password, dbname='postgres')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{database_name}"')
            print(f"✅ Database '{database_name}' created.")
        else:
            print(f"ℹ️ Database '{database_name}' already exists.")
        cur.close()
        conn.close()
    except psycopg2.DatabaseError as e:
        print(f"Error ensuring database {database_name} exists: {e}")
        raise

# --- Helper: Ensure table exists ---
def ensure_table_exists(conn, query, table_name):
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
        print(f"✅ Table '{table_name}' ready.")
    except psycopg2.DatabaseError as e:
        print(f"Error ensuring table {table_name} exists: {e}")
        raise
    

# --- Helper: Insert data ---
def insert_aws_cost_data(conn, data):
    try:
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
    except psycopg2.DatabaseError as e:
        print(f"Error inserting AWS cost data: {e}")
        raise

def insert_azure_cost_data(conn, data):
    try:
        cur = conn.cursor()
        for row in data:
            amount = row[0]
            date_obj = datetime.strptime(str(row[1]), "%Y%m%d")
            date = datetime.strftime(date_obj,"%Y-%m-%d")
            service_name = row[2]
            region = row[3]
            unit = row[4]
            cur.execute("""INSERT INTO azure_costs (date, region, service_name, amount, unit) VALUES (%s, %s, %s, %s, %s)""", (date, region, service_name, amount, unit))
        conn.commit()
        cur.close()
        print("✅ Azure data inserted successfully!")
    except psycopg2.DatabaseError as e:
        print(f"Error inserting Azure cost data: {e}")
        raise

def insert_gcp_cost_data(conn, data):
    pass



# Function to store AWS Cost Explorer summary to PostgreSQL port 5432 (simulated here as a JSON file)
def store_cost_data(json_data, query, table_name):
    # --- Main process ---
    if table_name == "aws_costs":
        conn = connect_db(database)
        ensure_table_exists(conn, query, table_name)
        insert_aws_cost_data(conn, json_data)
        conn.close()
    elif table_name == "azure_costs":
        conn = connect_db(azure_db_name)
        ensure_table_exists(conn, query, table_name)
        insert_azure_cost_data(conn, json_data)
        conn.close()
    elif table_name == "gcp_costs":
        conn = connect_db(gcp_db_name)
        ensure_table_exists(conn, query, table_name)
        insert_gcp_cost_data(conn, json_data)
        conn.close()
    else:
        print(f"❌ Unknown table name: {table_name}")

    print(f"🎉 In {table_name} cost data stored successfully.")

# --- Find last update date in the database ---
def get_last_update_date(db,query, table_name):
    conn = connect_db(db)
    ensure_table_exists(conn, query, table_name)
    try:
        with conn.cursor() as cur:
            stmt = sql.SQL("SELECT MAX(date) FROM {}").format(sql.Identifier(table_name))
            cur.execute(stmt)
            result = cur.fetchone()
            cur.close()
            return result[0] if result and result[0] else None
    finally:
        conn.close()






