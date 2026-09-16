from fastapi.testclient import TestClient
from main import app  # main.py dosyasındaki FastAPI app örneği

client = TestClient(app)


def test_reset_password_and_security_restriction():
    user_id = 1

    # 1. Adım: Şifre Sıfırlama (Soğuk Sıfırlama) Testi
    response = client.post("/api/v1/auth/reset-password", json={
        "user_id": user_id,
        "new_password": "SuperSecretNewPassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "ilk 24 saat" in data["message"]

    # 2. Adım: Şifre yenilendikten hemen sonra 24 saatlik hassas veri kısıtı testi (403 dönmeli)
    response_sensitive = client.get(f"/api/v1/user/sensitive-data/{user_id}")
    assert response_sensitive.status_code == 403
    assert "Güvenlik Kısıtı" in response_sensitive.json()["detail"]