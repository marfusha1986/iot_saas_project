from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api_routers import sensors,devices,tenants,security,auth
import oracledb



app = FastAPI(title="IoT SaaS Cloud Platform",version="1.0.0")
app.mount("/static",StaticFiles(directory="static"),name="static")


app.include_router(sensors.router)
app.include_router(devices.router)
app.include_router(tenants.router)
app.include_router(security.router)
app.include_router(auth.router)
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

