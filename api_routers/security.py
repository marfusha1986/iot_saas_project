from fastapi import APIRouter, HTTPException,UploadFile,File,Form
from database import get_db_connection
import os
import shutil

router = APIRouter(
    prefix="/security",
    tags=["AI Security $ Scans"]
)

UPLOAD_DIR ="uploads/media"
os.makedirs(UPLOAD_DIR,exist_ok=True)

@router.post("/scan")
async def upload_and_scan_media(
    device_id: str = Form(default="dev-001",description="Görüntüyü gönderen güvenlik kamerası ID"),
    tenant_id: int = Form(default=1,description="Tenant ID"),
    scan_type: str = Form(default="object_detention",description="AI tarama türü"),
    file: UploadFile = File(...)
):
    try:
        # 1.Dosyayı sunucuya kaydet
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2.Veritabanına kayıt(hangi cihaz,hangi dosya yolunu gönderdi gibi)
        connection = get_db_connection()
        cursor = connection.cursor()

        #device_scans ve benzeri tabloya log atıyoz
        sql = """
            INSERT INTO device_scans(device_id,
                                     tenant_id,
                                     scan_type,
                                     file_path,
                                     status)
                VALUES(:did,
                       :tid,
                       :stype,
                       :fpath,
                       :stat)
        """


        #Şimdilik tablo yok
        cursor.execute(sql,{
            "did":device_id,
            "tid":tenant_id,
            "stype":scan_type,
            "fpath":file_path,
            "stat":"Pending_AI_Analisis"
        })

        connection.commit()
        cursor.close()
        connection.close()

        #Yapay zeka modeli tetiklenecek

        ai_result = {
            "detected_objects":["human","unauthorized_entry_risk"],
            "confidence_score":0.94,
            "action_required":True
        }

        return {
            "status": "Success",
            "message": "Medya dosyası başarıyla yuklendı",
            "file_name":file.filename,
            "ai_analysis":ai_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media upload and scan error: {str(e)}")


