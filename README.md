

# 🏥 Bulut Tabanlı Randevu Yönetim Sistemi

Bu proje, **Bulut Bilişimde Sanallaştırma Teknolojilerine Giriş** dersi kapsamında geliştirilmiş, web tabanlı bir randevu yönetim sistemidir. Uygulama, **Docker** konteyner teknolojisi kullanılarak geliştirilmiş ve **Google Cloud Platform (GCP)** üzerinde çalışan bir **Compute Engine sanal makinesi** üzerinde dağıtılmıştır.

Projenin temel amacı, bulut bilişim ortamında sanallaştırma teknolojilerinin (Docker ve Virtual Machine) nasıl kullanıldığını uygulamalı olarak göstermektir.

---

## 🚀 Proje Özellikleri

Uygulama iki temel kullanıcı rolü üzerine kuruludur: **Kullanıcı (Hasta)** ve **Yönetici (Admin)**.

### 👤 Kullanıcı (Hasta)

* Kullanıcı kaydı ve giriş sistemi
* Klinik, bölüm ve doktora göre randevu alma
* Doktorun doluluk durumuna göre uygun saat önerileri
* Geçmiş ve gelecek randevuları görüntüleme
* Randevu durumlarını takip etme (Beklemede, Onaylı, İptal)

### 🛠 Yönetici (Admin)

* Tüm randevuları görüntüleme
* Randevuları onaylama, iptal etme veya silme
* Yeni klinik, bölüm ve doktor ekleme
* Randevuları duruma, tarihe veya doktora göre filtreleme
* Günlük ve toplam randevu istatistiklerini görüntüleme

---

## 🏗 Sistem Mimarisi

Proje, uygulama ve veritabanı olmak üzere **iki ayrı Docker konteyneri**nden oluşmaktadır. Bu konteynerler Docker ağı üzerinden birbiriyle haberleşmektedir.

### Kullanılan Teknolojiler

| Bileşen       | Teknoloji                              |
| ------------- | -------------------------------------- |
| Backend       | Python (Flask)                         |
| Veritabanı    | PostgreSQL                             |
| ORM           | SQLAlchemy                             |
| Sanallaştırma | Docker & Docker Compose                |
| Frontend      | HTML / CSS / JavaScript                |
| Bulut         | Google Cloud Platform (Compute Engine) |

---

## 📂 Veritabanı Yapısı

Sistem aşağıdaki ana tablolardan oluşmaktadır:

* **Users** → Kullanıcı bilgileri
* **Clinics** → Klinik bilgileri
* **Departments** → Kliniklere bağlı bölümler
* **Doctors** → Bölümlere bağlı doktorlar
* **Appointments** → Randevu bilgileri

Tablolar arasında **Foreign Key** ilişkileri kurulmuş ve veri bütünlüğü için **Unique** kısıtlamaları uygulanmıştır. Aynı doktora aynı saat için birden fazla randevu alınması engellenmiştir.

---

## ⚙️ Kurulum ve Çalıştırma

### Gereksinimler

* Docker
* Docker Compose

### 1️⃣ Repoyu Klonlayın

```bash
git clone https://github.com/kullaniciadiniz/bulut-tabanli-randevu-sistemi.git
cd bulut-tabanli-randevu-sistemi
```

### 2️⃣ Docker Compose ile Uygulamayı Başlatın

```bash
docker-compose up --build
```

Bu komut:

* Dockerfile kullanarak uygulama imajını oluşturur
* Flask uygulamasını ve PostgreSQL veritabanını başlatır

### 3️⃣ Uygulamaya Erişim

Tarayıcınızdan aşağıdaki adrese gidin:

```
http://localhost:5000
```

(Cloud ortamında çalıştırıyorsanız `localhost` yerine sunucu **External IP** adresini kullanın.)

---

## 🔐 Varsayılan Ayarlar

Varsayılan admin bilgileri Docker Compose ortam değişkenleri ile tanımlanmıştır:

* **Admin E-posta:** `admin@klinik.com`
* **Admin Şifre:** `admin123`

Veritabanı bağlantısı da yine ortam değişkenleri üzerinden yönetilmektedir.

---

## ☁️ Google Cloud Platform Dağıtımı

Proje, Google Cloud Platform üzerinde oluşturulan bir **Compute Engine sanal makinesi** üzerinde çalıştırılmıştır. Sanal makineye atanmış **External IP** sayesinde uygulama internet üzerinden erişilebilir hale gelmiştir.

---

## 📌 Sonuç

Bu proje ile Docker kullanılarak bir web uygulamasının konteyner haline getirilmesi ve Google Cloud Platform üzerinde çalıştırılması başarıyla gerçekleştirilmiştir. Proje, bulut bilişim ve sanallaştırma teknolojilerinin pratik kullanımını göstermektedir.

--

Söyle, GitHub için son halini birlikte mükemmelleştirelim 🚀
