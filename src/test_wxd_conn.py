import trino
import pandas as pd
import urllib3
import requests

# Disable SSL warnings (dev only)
urllib3.disable_warnings()

TRINO_USER = "ibmlhadmin"
TRINO_PASSWORD = "password"

# Custom session to inject LEGACY IBM header
session = requests.Session()
session.verify = False                       # self-signed cert
session.headers.update({
    "X-Presto-User": TRINO_USER              # REQUIRED by IBM /engine
})

conn = trino.dbapi.connect(
    host="localhost",
    port=8443,     # service port
    http_scheme="https",
    user=TRINO_USER,
    auth=trino.auth.BasicAuthentication(TRINO_USER, TRINO_PASSWORD),
    verify=False,
    catalog="iceberg_data",
    schema="gold"
)

conn._http_session = session
conn._http_session.base_url = "https://localhost:8443/engine"

cursor = conn.cursor()

# Test query
cursor.execute("SHOW CATALOGS")
print(cursor.fetchall())

cursor.execute("SHOW SCHEMAS FROM iceberg_data")
print(cursor.fetchall())

cursor.execute("SHOW TABLES FROM iceberg_data.gold")
print(cursor.fetchall())