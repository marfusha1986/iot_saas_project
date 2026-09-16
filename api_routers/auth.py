from datetime import datetime,timedelta

from fastapi import FastAPI,HTTPException,APIRouter,BackgroundTasks
from oracledb import cursor
from pydantic import BaseModel
from typing import List

from starlette.background import BackgroundTask

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

class ResetPasswordSchema(BaseModel):
    user_id: int
    new_password: str

@router.post("/validate/keystroke")
def validate_keystroke(payload: ValidateRequest):
    """
    Kilitli hesabı açmak veya kimlik doğrulamak için
     millisaniye tabanlı tuş vuruşu dinamiklerini test eden uç nokta.
    """

    connection = get_db_connection()
    curaor = connection.cursor()

    try:
        # 1.Kullanıcının kilitli olup olmadığını kontrol et
        cursor.execute('SELECT "FAİLED_ATTEMPTS" FROM "USER_PROFİLES" WHERE "USER_ID" = :1',[payload.user_id])
        profile = cursor.fetchone()
        if not profile:
            raise HTTPException(status_code=404,detail="Kullanıcı profili bulunamadı!")

        failed_attempts = profile[0] or 0
        if failed_attempts >= 3:
            #Sistem kilitli,milisaniye analizi ile hak doğrulaması yap
            pass

        # 2.Millisaaniye Sapma analizi (Keystroke Dynamics Engine)

        is_authenticated = KeystrokeAuthEngine.calculate_deviation(
            payload.baseline_times,
            payload.current_times
        )

        if not is_authenticated:
            raise HTTPException(
            status_code=401,
            detail="Biyometric doğrulama başarısız: Sapma çok yüksek!"
            )

        #3. Doğrulama başarılıysa kilitli sayacı sıfırla (Kilidi Kalfır)
        cursor.execute(
            'UPDATE "USER_PROFILES" SET "FAILED_ATTEMPTS" = 0 WHERE "USER_ID" = :1',
            [payload.user_id]
        )
        connection.commit()

        return{
            "status":"success",
            "user_id":payload.user_id,
            "verified":True,
            "message":"Kullanıcı başarıyla doğrulandı."
            }
    except HTTPException as he:
        raise he
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500,detail=f"Doğrulama hatası:{str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.post("/register/baseline")
async def register_baseline(payload: BaselineRegisterSchema,verified:bool = False):

    """
    Baseline kayıt ve güncelleme uç noktası.
    3hatalı denemede kilitlenir,ancak "verified = True" (millisaniye doğrulamasından geçmişse) doğrulanır.

    """

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
                    status_code=423,#Locked
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

def send_security_alert_notification(user_id:int):
    """
    Kullanıcının cep telefonuna /e-postasına phishing riskine karşı güvenli bilgilendirme ve
     bildirim uçuran simulasyon fonksiyon
   """
    #Burada gercek sms/push notification servisleri(Twilio,Firebase) tetiklenir
    print(f"[SECURİTY ALERT] Kullanıcı Id {user_id}: Şifreniz sıfırlandı.Bu siz değilseniz lütfen resmi uygulamadan kontrol edin.")

@router.post("/auth/reset-password")
def reset_password(payload: ResetPasswordSchema, background_tasks: BackgroundTasks):
    """
    Kullanıcı şifresini tamamen unuttuğunda (veya milisaniye ritmini hatırlamadığında)
    gerçekleşen 'Soğuk Sıfırlama' ve 24 saatlik güvenlik kısıtı uç noktası.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # 1. Kullanıcının varlığını kontrol et
        cursor.execute('SELECT "USER_ID" FROM "USER_PROFILES" WHERE "USER_ID" = :1', [payload.user_id])
        profile = cursor.fetchone()

        if not profile:
            raise HTTPException(status_code=404, detail="Kullanıcı profili bulunamadı.")

        # 2. Şifreyi sıfırla, baseline'ı temizle (yeni ritim için sıfırdan öğrenilecek),
        # FAILED_ATTEMPTS sayacını sıfırla ve 24 saatlik veri erişim kısıtı (RESTRICTED_UNTIL) koy.
        update_query = """
            UPDATE "USER_PROFILES" 
            SET "BASELINE_VECTOR" = NULL, 
                "FAILED_ATTEMPTS" = 0, 
                "RESTRICTED_UNTIL" = CURRENT_TIMESTAMP + INTERVAL '1' DAY,
                "UPDATED_AT" = CURRENT_TIMESTAMP
            WHERE "USER_ID" = :1
        """
        cursor.execute(update_query, [payload.user_id])
        connection.commit()

        # 3. Müşteriyi boğmadan, arka planda güvenli bilgilendirme (Push/SMS) tetikle
        background_tasks.add_task(send_security_alert_notification, payload.user_id)

        return {
            "status": "success",
            "user_id": payload.user_id,
            "message": "Şifreniz başarıyla yenilendi. Güvenliğiniz için ilk 24 saat hassas verilere erişim kısıtlanmıştır ve telefonunuza bilgilendirme gönderilmiştir."
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Şifre sıfırlama hatası: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.get("/user/sensitive-data/{user_id}")
def get_sensitive_data(user_id: int):
    """
    Fatura, garanti belgesi gibi hassas verilere erişim kapısı.
    24 saatlik kısıt süresi dolmuş mu diye kontrol eder.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT "RESTRICTED_UNTIL" FROM "USER_PROFILES" WHERE "USER_ID" = :1', [user_id])
        profile = cursor.fetchone()

        if not profile:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

        restricted_until = profile[0]

        # Eğer kısıt süresi hala devam ediyorsa
        if restricted_until and restricted_until > datetime.now():
            raise HTTPException(
                status_code=403,
                detail="Güvenlik Kısıtı: Şifreniz yeni değiştirildiği için ilk 24 saat hassas verilere erişim geçici olarak kısıtlanmıştır."
            )

        return {
            "status": "success",
            "data": "Hassas faturalar ve belgeler listeleniyor..."
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()