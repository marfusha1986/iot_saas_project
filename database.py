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

def get_baseliine_from_db(user_id:int) -> list[float] | None:
    """
    Oracle 23c veritabanından ilgili kullanıcının baseline vektörünü çeksin
    :param user_id:
    :return:
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT baseline_vector FROM user_profiles WHERE user_id = :uid"
        cursor.execute(query,uid=user_id)

        row = cursor.fetchone()
        cursor.close()
        connection.close()

        if row and row[0]:
            vector_str = row[0]
            return [float(val.strip()) for val in vector_str.split(",")]

        return None

    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None
