import psycopg2
conn_details = {
    "dbname": "okzegkwz", 
    "user": "okzegkwz",
    "password": "7UwFflnPy3byudSr32K1ugHniRSVK6v_",
    "host": "kandula.db.elephantsql.com",
    "port": "5432"
}
try:
    conn = psycopg2.connect(**conn_details)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
