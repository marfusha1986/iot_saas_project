# 🛡️ Secure Keystroke Biometric Authentication & Account Takeover (ATO) Protection Engine

Modern web uygulamalarında ve e-ticaret platformlarında kritik bir ikilem yaşanır: **Yapay zeka/bot saldırılarını** engellemek mi, yoksa aşırı güvenlik önlemleriyle **gerçek müşteriyi bürokratik engellerle kaçırmak (Churn)** mı? 

Bu proje; milisaniye tabanlı davranışsal biyometriyi ve akıllı kurtarma akışlarını harmanlayarak, **kullanıcıyı asla boğmayan ama siber saldırganlara göz açtırmayan** kurumsal seviyede bir kimlik doğrulama motorudur.

---

## 🚀 Öne Çıkan Mimari ve Güvenlik Özellikleri

1. **Milisaniye Tabanlı Tuş Vuruşu Dinamikleri (`KeystrokeAuthEngine`):**
   * Kullanıcının klavye ritmini (`dwell` ve `flight` süreleri) analiz eder. Botları ve çalınmış statik şifrelerle sisteme sızmaya çalışan AI ajanlarını etkisiz hale getirir.
2. **Kademeli Kilitlenme ve Kurtarma:**
   * 3 hatalı denemede hesap güvenli bir şekilde kilitlenir (`423 Locked`).
   * Kilit sonrası ilk bariyer milisaniye ritmiyle yapılan şeffaf doğrulamadır (`/validate/keystroke`).
3. **Güvenli "Soğuk Sıfırlama" (Cold Reset):**
   * Kullanıcı ritmini tamamen unuttuğunda devreye giren şifre yenileme akışı (`/auth/reset-password`).
4. **Anti-Phishing & Out-of-Band Bildirimleri:**
   * Oltalama (phishing) tuzaklarına yol açacak sahte "linklere tıklayın" uyarıları yerine, güvenli kanallardan (`BackgroundTasks`) push/SMS bilgilendirmeleri tetiklenir.
5. **24 Saatlik Hassas Veri Kısıtı (Security Restriction):**
   * Şifresi sıfırlanan bir hesabın arkasındaki finansal veriler, faturalar ve belgeler **ilk 24 saat boyunca** (`RESTRICTED_UNTIL`) dışarıdan gelebilecek olası hesap ele geçirme (ATO) risklerine karşı otomatik olarak kilit altında tutulur.

---

## 🛠️ Teknoloji Yığını

* **Backend:** FastAPI (Python 3.14+)
* **Veritabanı:** Oracle Database 23c
* **Test Altyapısı:** Pytest, HTTPX, TestClient
* **Mimari Desenler:** Defense in Depth, Behavioral Biometrics, Async Background Tasks

---

## 📦 Kurulum ve Çalıştırma

1. **Projeyi Klonlayın:**
   ```bash
   git clone <repo-url>
   cd iot_saas_project