from fastapi import APIRouter,HTTPException
from database import get_db_connection
from models import DeviceCreatePayload

router = APIRouter(
    prefix="/devices",
    tags=["Devices"]
)

@router.post("/")
def register_device(device: DeviceCreatePayload):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        sql="""
        INSERT INTO devices (device_id,
                             tenant_id,
                             user_id,
                             device_name,
                             status) 
            VALUES (:device_id, :tenant_id,:user_id, :device_name, :status)
            """
        cursor.execute(sql,{
             "device_id":device.device_id,
            "tenant_id":device.tenant_id,
            "user_id":device.user_id,
            "device_name":device.device_name,
            "status":device.status
        })
        connection.commit()
        cursor.close()
        connection.close()

        return {
            "status": "Success",
            "message": "Yeni IoT cihazı bulut sistemine kaydedildi.",
            "device": device
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cihaz kayıt hatası:{str(e)}")