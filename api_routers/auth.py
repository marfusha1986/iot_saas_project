from fastapi import FastAPI,HTTPException,APIRouter
from pydantic import BaseModel
from typing import List

from database import get_db_connection
from services.auth_engine import KeystrokeAuthEngine


router = APIRouter(prefix="/api/v1", tags=["Authentication"])

class BaselineRegisterSchema(BaseModel):
    user_id : int
    baseline_vector: List[float]

class ValidateRequest(BaseModel):
    user_id:int
    baseline_times: List[float]
    current_times: List[float]

@router.post("/validate/keystroke")
def validate_keystroke(payload: ValidateRequest):
    #Simule edilmiş baseline kontrolü
    is_authenticated = KeystrokeAuthEngine.calculate_deviation(
        payload.baseline_times,
        payload.current_times
    )

    if not is_authenticated:
        raise HTTPException(
            status_code=401,
            detail="Biyometric doğrulama başarısız: Sapma çok yüksek!"
        )
    return{
            "status":"success",
            "user_id":payload.user_id,
            "message":"Kullanıcı başarıyla doğrulandı."
    }

@router.post("/register/baseline")
async def register_baseline(payload: BaselineRegisterSchema,verified:bool = False):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        #1.Kullanıcının önceden kaydı varmı diye kontrol et
        cursor.execute('SELECT "BASELINE_VECTOR" ,"FAILED_ATTEMPTS" FROM "USER_PROFILES" WHERE "USER_ID" = :1',[payload.user_id])
        profile = cursor.fetchone()

        if profile and not verified:
            baseline_vec,failed_attempts = profile[0],profile[1] or 0

            #Eğer 3 kez yanlış deneyip bloklandıysa kimlik doğrulama zorla
            if failed_attempts >= 3 and not verified:
                raise HTTPException(
                    status_code=403,
                    detail="Çok fazla başarısız deneme.Hesap kilitlendi!"
                )
            if not verified:
                #Başarısız deneme saysını 1 arttır
                cursor.execute('UPDATE "USER_PROFILES" SET "FAILED_ATTEMPTS" = "FAILED_ATTEMPTS" +1 WHERE "USER_ID" = :1',
                           [payload.user_id])
                connection.commit()
            # 2 ve 3. Kayıt varsa kimlik doğrulanmadan MERGE yapılamaz!

                raise HTTPException(
                    status_code=403,
                    detail= f"Yetkisiz Güncelleme denemesi.Kalan hak: {max(0, 2-failed_attempts)}"
                )

        vector_str = ", ".join(map(str, payload.baseline_vector))

        # 4 İlk kayıt veya başarıyla doğrulanmıs güncelleme MERGE
        query = """
            MERGE INTO "USER_PROFILES" p
            USING (SELECT :1 AS u_id, :2 AS vec FROM dual) s
            ON (p."USER_ID" = s.u_id)
            WHEN MATCHED THEN
              UPDATE SET p."BASELINE_VECTOR" = s.vec, p.updated_at = CURRENT_TIMESTAMP
            WHEN NOT MATCHED THEN
              INSERT ("USER_ID", "BASELINE_VECTOR") VALUES (s.u_id, s.vec)
        """

        cursor.execute(query,[payload.user_id,vector_str])
        connection.commit()

        cursor.close()
        connection.close()

        return{
            "status": "succcess",
            "user_id": payload.user_id,
            "message": "Kullanıcı biyometrik baseline verisi başarıyla kaydedildi."
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        connection.rollback()
        raise HTTPException(status_code=500,detail=f"Kayıt hatası:{str(e)}")
    finally:
        cursor.close()
        connection.close()