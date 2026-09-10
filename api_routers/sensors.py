from fastapi import APIRouter,HTTPException
from database import get_db_connection
from models import SensorDataPayload

router = APIRouter(prefix="/sensors",tags=["Sensors"])

@router.post("/data")
def receive_sensor_data(data: SensorDataPayload):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        sql = """
            INSERT INTO sensor_data (device_id, metric_name, metric_value)
            VALUES (:did, :mname, :mval)
        """
        cursor.execute(sql, {
            "did": data.device_id,
            "mname": data.metric_name,
            "mval": data.metric_value
        })
        connection.commit()

        cursor.close()
        connection.close()

        return {
            "status": "Success",
            "message": "Sensor data received and stored successfully.",
            "data":data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store sensor data: {str(e)}")

@router.get("/data")
def get_sensor_data():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        sql = ("SELECT data_id, device_id,metric_name, metric_value,recorded_at"
               " FROM sensor_data"
               " ORDER BY recorded_at DESC")
        cursor.execute(sql)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "data_id": row[0],
                "device_id": row[1],
                "metric_name": row[2],
                "metric_value": row[3],
                "recorded_at": row[4]
            })

        cursor.close()
        connection.close()

        return {
            "status": "Success",
            "count": len(result),
            "data": [
                {"device_id": row[0], "metric_name": row[1], "metric_value": row[2]} for row in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sensor data: {str(e)}")