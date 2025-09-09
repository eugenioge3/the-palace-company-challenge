import os
from dagster import resource
from sqlalchemy import create_engine

@resource
def mysql_connection_resource(_):
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    db = os.getenv("MYSQL_DATABASE")
    port = os.getenv("MYSQL_PORT")

    conn_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(conn_url)
    yield engine

mysql_etl_resource = mysql_connection_resource