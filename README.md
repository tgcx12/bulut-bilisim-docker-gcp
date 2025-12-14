
# 🏥 Bulut Tabanlı Randevu Yönetim Sistemi

[cite_start]Bu proje, **Bulut Bilişimde Sanallaştırma Teknolojilerine Giriş** kapsamında geliştirilmiş web tabanlı bir randevu yönetim uygulamasıdır[cite: 1, 4]. [cite_start]Uygulama, **Docker** konteyner teknolojisi kullanılarak geliştirilmiş ve **Google Cloud Platform (GCP)** Compute Engine üzerinde çalışan bir sanal makineye dağıtılmıştır[cite: 10, 11].

[cite_start]Projenin temel amacı, bulut bilişim ortamında sanallaştırma teknolojilerinin (Docker & Virtual Machine) pratik kullanımını ve avantajlarını göstermektir[cite: 27, 31].

## 🚀 Proje Özellikleri

Uygulama, Kullanıcı ve Yönetici (Admin) olmak üzere iki temel rol üzerine kurgulanmıştır:

### 👤 Kullanıcı (Hasta) Modülü
* [cite_start]**Kayıt ve Giriş:** Güvenli oturum yönetimi ve kullanıcı kaydı[cite: 30, 154].
* [cite_start]**Dinamik Randevu Alma:** Klinik, Bölüm ve Doktor hiyerarşisine göre dinamik seçim yapabilme[cite: 157].
* [cite_start]**Akıllı Saat Önerisi:** Seçilen doktorun doluluk durumuna göre yalnızca uygun saat aralıklarının listelenmesi[cite: 30, 176].
* [cite_start]**Randevu Takibi:** Geçmiş ve gelecek randevuların durumunu (Beklemede, Onaylı, İptal) görüntüleme[cite: 180].

### 🛠 Yönetici (Admin) Paneli
* [cite_start]**Dashboard:** Toplam, günlük ve bekleyen randevu istatistikleri[cite: 189].
* [cite_start]**Randevu Yönetimi:** Randevuları onaylama, iptal etme veya silme işlemleri[cite: 160, 192].
* [cite_start]**Veri Yönetimi:** Sisteme yeni Klinik, Bölüm ve Doktor ekleyebilme[cite: 196].
* [cite_start]**Filtreleme:** Randevuları duruma, doktora veya tarihe göre filtreleyerek görüntüleme[cite: 190, 191].

## 🏗 Sistem Mimarisi ve Teknolojiler

Proje, **mikroservis** mimarisine benzer bir yapıda, uygulama ve veritabanı olmak üzere iki ayrı konteynerden oluşmaktadır. [cite_start]Bu konteynerler dahili bir ağ üzerinden haberleşir[cite: 26, 66].

| Bileşen | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Backend / Web** | Python (Flask) | [cite_start]Uygulama mantığı ve API uç noktaları[cite: 44]. |
| **Veritabanı** | PostgreSQL | [cite_start]İlişkisel veri tutarlılığı için kullanılmıştır[cite: 69, 75]. |
| **Sanallaştırma** | Docker & Compose | [cite_start]Uygulama ve veritabanının izole çalıştırılması[cite: 42]. |
| **ORM** | SQLAlchemy | [cite_start]Veritabanı nesne-ilişkisel eşleşmesi[cite: 77]. |
| **Frontend** | HTML/CSS/JS | [cite_start]Kullanıcı arayüzü[cite: 44, 174]. |
| **Cloud** | Google Cloud (GCP) | [cite_start]Compute Engine VM üzerinde barındırma[cite: 41, 201]. |

### 📂 Veritabanı Yapısı
[cite_start]Sistem `Users`, `Clinics`, `Departments`, `Doctors` ve `Appointments` olmak üzere 5 ana tablodan oluşur[cite: 83]. [cite_start]Veri bütünlüğü için *Foreign Key* ve *Unique* kısıtlamaları uygulanmıştır[cite: 110, 115].

## ⚙️ Kurulum ve Çalıştırma (Local & Docker)

[cite_start]Projeyi kendi bilgisayarınızda veya bir sunucuda çalıştırmak için Docker'ın yüklü olması yeterlidir[cite: 210].

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullaniciadiniz/randevu-yonetim-sistemi.git](https://github.com/kullaniciadiniz/randevu-yonetim-sistemi.git)
    cd randevu-yonetim-sistemi
    ```

2.  **Docker Compose ile Ayağa Kaldırın:**
    Uygulama ve veritabanını tek komutla başlatmak için:
    ```bash
    docker-compose up --build
    ```
    [cite_start]*Bu işlem `Dockerfile` kullanılarak imajı oluşturacak ve `docker-compose.yml` dosyasındaki konfigürasyona göre servisleri başlatacaktır[cite: 205, 211].*

3.  **Uygulamaya Erişim:**
    Tarayıcınızdan aşağıdaki adrese gidin:
    * **Web Arayüzü:** `http://localhost:5000` (veya sunucu IP adresiniz).

### 🔐 Varsayılan Konfigürasyon
[cite_start]Proje varsayılan olarak aşağıdaki veritabanı bağlantı ayarlarını kullanır[cite: 78]:
* **DB Host:** `db` (Docker servis adı)
* **DB User:** `app`
* **DB Password:** `app123`
* **DB Name:** `randevu`

[cite_start]*Not: Veritabanı verileri Docker Volume (`DB Volume`) sayesinde kalıcıdır, konteyner kapatılsa bile veriler kaybolmaz[cite: 70, 214].*

## ☁️ Google Cloud Platform (GCP) Dağıtımı

[cite_start]Bu proje GCP üzerinde şu adımlarla test edilmiştir[cite: 203, 204]:
1.  GCP Compute Engine üzerinde bir **Sanal Makine (VM)** oluşturuldu.
2.  VM'e dış IP atandı ve güvenlik duvarından (Firewall) HTTP trafiğine izin verildi.
3.  VM içine Docker ve Docker Compose kuruldu.
4.  Proje dosyaları VM'e çekilerek konteynerler çalıştırıldı.

## 📝 Gelecek Çalışmalar
* HTTPS entegrasyonu ve Ters Vekil (Reverse Proxy) kullanımı.
* Kubernetes ile otomatik ölçeklendirme.
* [cite_start]Cloud SQL gibi yönetilen veritabanı servislerine geçiş[cite: 221].

## 👤 Yazar
**Tuğçe Gül**
* [cite_start]Kocaeli Üniversitesi - Bilişim Sistemleri Mühendisliği [cite: 2, 4]
* [cite_start]✉️ İletişim: 221307036@kocaeli.edu.tr [cite: 6]

---
*Bu proje akademik bir çalışma kapsamında geliştirilmiştir.*
