from fastapi import APIRouter,HTTPException
from database import get_db_connection
from models import TenantCreatePayload

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)

@router.post("/")
def register_tenant(tenant: TenantCreatePayload):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        sql = """
            INSERT INTO tenants ( company_name, subdomain)
            VALUES (:cname, :sub)
        """
        cursor.execute(sql, {
            "cname": tenant.tenant_name,
            "sub": tenant.subdomain
        })
        connection.commit()

        cursor.close()
        connection.close()

        return {
            "status": "Success",
            "message": "Yeni tenant bulut sistemine kaydedildi."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tenant kayıt hatası: {str(e)}")