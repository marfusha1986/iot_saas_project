from fastapi import FastAPI,HTTPException
from api_routers import sensors,devices,tenants,security
import oracledb



app = FastAPI(title="IoT SaaS Cloud Platform",version="1.0.0")


app.include_router(sensors.router)
app.include_router(devices.router)
app.include_router(tenants.router)
app.include_router(security.router)
@app.get("/")
def read_root():
    return {"message":"Modüler IoT SaaS Altyapısı çalışıyor!"}

