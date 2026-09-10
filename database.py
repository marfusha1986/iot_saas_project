import oracledb

DB_USER = "iot_saas"
DB_PASSWORD = "HamzaMelek02"
DB_DSN = "localhost:1521/FREEPDB1"

def get_db_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )