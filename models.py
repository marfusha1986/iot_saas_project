from pydantic import BaseModel,Field
from typing import Optional

class SensorDataPayload(BaseModel):
    device_id:str
    metric_name:str
    metric_value:float

class DeviceCreatePayload(BaseModel):
    device_id: str = Field(default="dev_001", description="Cihaz ID")
    device_name: str = Field(default="Sicaklik Sensoru", description="Cihaz adı")
    tenant_id: int = Field(default=1, description="Veritabanındaki geçerli Tenant ID")
    user_id: int = Field(default=1, description="Veritabanındaki geçerli User ID")
    status: str = Field(default="ACTIVE", description="Cihaz durumu")

class TenantCreatePayload(BaseModel):
    tenant_name:str=Field(default="Test Tenant", description="Tenant name")
    subdomain:str=Field(default="test-sub-1", description="Unique subdomain")

class SecurityScanPayload(BaseModel):
    device_id: str = Field(default="dev_001", description="Associated device ID")
    tenant_id: int=Field(default=1,description="Associated tenant ID")
    scan_type:str=Field(default="Object Detection", description="Yapay zeka tarama türü: object_detection, face_recognition, anomaly_detection")