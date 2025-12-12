from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os, time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql://app:app123@db:5432/randevu"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@klinik.com").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123").strip()


# ---------------- MODELS ----------------

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)

    first_name = db.Column(db.String(60), nullable=True)
    last_name = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(30), nullable=True)

    role = db.Column(db.String(20), nullable=False, default="user")  # user/admin

    @property
    def full_name(self):
        fn = (self.first_name or "").strip()
        ln = (self.last_name or "").strip()
        name = (fn + " " + ln).strip()
        return name or self.email


class Clinic(db.Model):
    __tablename__ = "clinics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)


class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    clinic_id = db.Column(db.Integer, db.ForeignKey("clinics.id"), nullable=False)
    clinic = db.relationship("Clinic", backref=db.backref("departments", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("clinic_id", "name", name="uq_department_clinic_name"),
    )


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    department = db.relationship("Department", backref=db.backref("doctors", lazy=True))


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("appointments", lazy=True))

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    doctor = db.relationship("Doctor", backref=db.backref("appointments", lazy=True))

    start_at = db.Column(db.DateTime, nullable=False, index=True)
    note = db.Column(db.String(300), nullable=True)

    # pending / confirmed / cancelled
    status = db.Column(db.String(20), nullable=False, default="pending")

    # aynı doktor + aynı saat => tek kayıt (pending de dolu sayılır)
    __table_args__ = (
        db.UniqueConstraint("doctor_id", "start_at", name="uq_doctor_startat"),
    )


# ---------------- DB INIT ----------------

def db_init():
    retries = 10
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
            print("✅ DB hazır")
            return
        except Exception as e:
            print("⏳ DB bekleniyor...", e)
            time.sleep(3)
            retries -= 1
    raise RuntimeError("❌ DB bağlantısı kurulamadı")


# ---------------- UTILS ----------------

def require_admin() -> bool:
    return session.get("role") == "admin"

def current_user():
    email = (session.get("user_email") or "").strip().lower()
    if not email:
        return None
    return User.query.filter_by(email=email).first()

def combine_date_time(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

def generate_slots(start="09:00", end="17:00", step_min=30):
    fmt = "%H:%M"
    t = datetime.strptime(start, fmt)
    endt = datetime.strptime(end, fmt)
    slots = []
    while t <= endt:
        slots.append(t.strftime(fmt))
        t += timedelta(minutes=step_min)
    return slots


# ---------------- AUTH ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = (request.form.get("first_name") or "").strip()
        last_name  = (request.form.get("last_name") or "").strip()
        phone      = (request.form.get("phone") or "").strip()
        email      = (request.form.get("email") or "").strip().lower()
        password   = (request.form.get("password") or "").strip()

        if not first_name or not last_name or not email or not password:
            return render_template("register.html", error="Lütfen tüm zorunlu alanları doldurun.")

        if email == ADMIN_EMAIL:
            return render_template("register.html", error="Bu e-posta admin için ayrılmış.")

        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Bu e-posta zaten kayıtlı. Giriş yapın.")

        u = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role="user"
        )
        db.session.add(u)
        db.session.commit()

        session["role"] = "user"
        session["user_email"] = email
        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()

        if not email or not password:
            return render_template("login.html", error="E-posta ve şifre gerekli.")

        # ADMIN
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["role"] = "admin"
            session["user_email"] = email
            return redirect("/admin")

        # USER
        u = User.query.filter_by(email=email).first()
        if not u:
            return render_template("login.html", error="Kullanıcı bulunamadı. Önce kayıt olun.")
        if not u.password_hash or not check_password_hash(u.password_hash, password):
            return render_template("login.html", error="Şifre hatalı.")

        session["role"] = "user"
        session["user_email"] = email
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- API ----------------

@app.route("/api/clinics")
def api_clinics():
    clinics = Clinic.query.order_by(Clinic.name.asc()).all()
    return jsonify([{"id": c.id, "name": c.name} for c in clinics])

@app.route("/api/departments")
def api_departments():
    clinic_id = request.args.get("clinic_id", type=int)
    q = Department.query
    if clinic_id:
        q = q.filter_by(clinic_id=clinic_id)
    deps = q.order_by(Department.name.asc()).all()
    return jsonify([{"id": d.id, "name": d.name, "clinic_id": d.clinic_id} for d in deps])

@app.route("/api/doctors")
def api_doctors():
    clinic_id = request.args.get("clinic_id", type=int)
    department_id = request.args.get("department_id", type=int)

    q = Doctor.query.join(Department)
    if department_id:
        q = q.filter(Doctor.department_id == department_id)
    if clinic_id:
        q = q.filter(Department.clinic_id == clinic_id)

    docs = q.order_by(Doctor.full_name.asc()).all()
    return jsonify([{
        "id": d.id,
        "name": d.full_name,
        "department_id": d.department_id,
        "clinic_id": d.department.clinic_id
    } for d in docs])

@app.route("/suggestions")
def suggestions():
    date = (request.args.get("date") or "").strip()
    doctor_id = request.args.get("doctor_id", type=int)
    if not date or not doctor_id:
        return jsonify({"suggestions": []})

    day_start = datetime.strptime(date, "%Y-%m-%d")
    day_end = day_start + timedelta(days=1)

    busy = {a.start_at for a in Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_at >= day_start,
        Appointment.start_at < day_end,
        Appointment.status != "cancelled",
    ).all()}

    free = []
    for s in generate_slots(step_min=30):
        dt = combine_date_time(date, s)
        if dt not in busy:
            free.append(s)

    return jsonify({"suggestions": free[:12]})


# ---------------- USER PAGE ----------------

@app.route("/", methods=["GET", "POST"])
def user_home():
    if session.get("role") not in ("user", "admin"):
        return redirect("/login")

    u = current_user()
    if session.get("role") == "user" and not u:
        return redirect("/login")

    clinics = Clinic.query.order_by(Clinic.name.asc()).all()
    mesaj, hata = "", ""

    if request.method == "POST":
        if not u:
            hata = "Lütfen önce giriş yapın."
        else:
            clinic_id = request.form.get("clinic_id", type=int)
            department_id = request.form.get("department_id", type=int)
            doctor_id = request.form.get("doctor_id", type=int)
            date = (request.form.get("date") or "").strip()
            time_str = (request.form.get("time") or "").strip()
            note = (request.form.get("note") or "").strip()

            if not clinic_id or not department_id or not doctor_id or not date or not time_str:
                hata = "Klinik, bölüm, doktor, tarih ve saat seçiniz."
            else:
                doc = Doctor.query.get(doctor_id)
                if not doc:
                    hata = "Doktor bulunamadı."
                elif doc.department_id != department_id:
                    hata = "Seçilen doktor bu bölüme ait değil."
                elif doc.department.clinic_id != clinic_id:
                    hata = "Seçilen bölüm bu kliniğe ait değil."
                else:
                    start_at = combine_date_time(date, time_str)
                    existing = Appointment.query.filter_by(doctor_id=doctor_id, start_at=start_at).first()
                    if existing and existing.status != "cancelled":
                        hata = "Bu saat dolu. Lütfen başka saat seçin."
                    else:
                        a = Appointment(user_id=u.id, doctor_id=doctor_id, start_at=start_at, note=note, status="pending")
                        db.session.add(a)
                        db.session.commit()
                        return redirect("/")  # refresh-safe

    my_appointments = []
    soon_list = []
    if u:
        my_appointments = Appointment.query.filter_by(user_id=u.id).order_by(Appointment.start_at.desc()).limit(30).all()
        now = datetime.now()
        soon_list = [a for a in my_appointments if a.status != "cancelled" and now <= a.start_at <= now + timedelta(hours=1)]

    return render_template(
        "index.html",
        clinics=clinics,
        my_appointments=my_appointments,
        mesaj=mesaj,
        hata=hata,
        soon_list=soon_list,
        user=u
    )


# ---------------- ADMIN PANEL ----------------

@app.route("/admin")
def admin():
    if not require_admin():
        return redirect("/login")

    status = (request.args.get("status") or "all").strip().lower()
    q = (request.args.get("q") or "").strip().lower()

    query = Appointment.query
    if status != "all":
        query = query.filter(Appointment.status == status)

    appointments = query.order_by(Appointment.start_at.desc()).all()

    if q:
        def ok(a: Appointment):
            return (
                q in (a.user.email or "").lower()
                or q in (a.user.full_name or "").lower()
                or q in (a.doctor.full_name or "").lower()
                or q in (a.doctor.department.name or "").lower()
                or q in (a.doctor.department.clinic.name or "").lower()
                or q in (a.status or "").lower()
                or q in a.start_at.strftime("%Y-%m-%d %H:%M")
            )
        appointments = [a for a in appointments if ok(a)]

    today = datetime.now().date()
    total = Appointment.query.count()
    today_count = Appointment.query.filter(
        Appointment.start_at >= datetime.combine(today, datetime.min.time()),
        Appointment.start_at < datetime.combine(today + timedelta(days=1), datetime.min.time()),
    ).count()
    pending_count = Appointment.query.filter_by(status="pending").count()

    clinics = Clinic.query.order_by(Clinic.name.asc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()
    doctors = Doctor.query.order_by(Doctor.full_name.asc()).all()

    # ✅ Hasta listesi (admin panelde göstermek için)
    patients = User.query.filter(User.role == "user").order_by(User.id.desc()).all()

    return render_template(
        "admin.html",
        appointments=appointments,
        total=total,
        today_count=today_count,
        pending_count=pending_count,
        status=status,
        q=request.args.get("q", ""),
        clinics=clinics,
        departments=departments,
        doctors=doctors,
        patients=patients
    )

@app.route("/admin/update/<int:aid>", methods=["POST"])
def admin_update(aid):
    if not require_admin():
        return redirect("/login")

    action = (request.form.get("action") or "").strip()
    a = Appointment.query.get_or_404(aid)

    if action == "confirm":
        a.status = "confirmed"
    elif action == "cancel":
        a.status = "cancelled"
    elif action == "delete":
        db.session.delete(a)
        db.session.commit()
        return redirect(url_for("admin"))

    db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/clinic/add", methods=["POST"])
def admin_add_clinic():
    if not require_admin():
        return redirect("/login")

    # ✅ admin.html "clinic_name" gönderiyor, burada ikisini de kabul ediyoruz
    name = (request.form.get("clinic_name") or request.form.get("name") or "").strip()
    if name and not Clinic.query.filter_by(name=name).first():
        db.session.add(Clinic(name=name))
        db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/department/add", methods=["POST"])
def admin_add_department():
    if not require_admin():
        return redirect("/login")

    name = (request.form.get("department_name") or request.form.get("name") or "").strip()
    clinic_id = request.form.get("clinic_id", type=int)
    if not name or not clinic_id:
        return redirect(url_for("admin"))

    clinic = Clinic.query.get(clinic_id)
    if not clinic:
        return redirect(url_for("admin"))

    exists = Department.query.filter_by(clinic_id=clinic_id, name=name).first()
    if not exists:
        db.session.add(Department(name=name, clinic_id=clinic_id))
        db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/doctor/add", methods=["POST"])
def admin_add_doctor():
    if not require_admin():
        return redirect("/login")

    full_name = (request.form.get("doctor_name") or request.form.get("name") or "").strip()
    department_id = request.form.get("department_id", type=int)
    if not full_name or not department_id:
        return redirect(url_for("admin"))

    dep = Department.query.get(department_id)
    if not dep:
        return redirect(url_for("admin"))

    db.session.add(Doctor(full_name=full_name, department_id=department_id))
    db.session.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    db_init()
    app.run(host="0.0.0.0", port=5000)
