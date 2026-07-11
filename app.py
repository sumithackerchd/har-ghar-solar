from flask import (
    Flask, render_template, request, redirect,
    session, send_file, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from openpyxl.utils import get_column_letter
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd
import io, os, sqlite3
from openpyxl.worksheet.table import Table, TableStyleInfo
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# ==========================
# AZURE
# ==========================
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

load_dotenv()

configure_azure_monitor(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)
import logging
logger = logging.getLogger("hargharsolar")
logger.setLevel(logging.INFO)

# ==========================
# UTTAR PRADESH 75 DISTRICTS
# ==========================
UP_DISTRICTS = [
    "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha",
    "Auraiya", "Ayodhya", "Azamgarh", "Baghpat", "Bahraich",
    "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly",
    "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr",
    "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah",
    "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar",
    "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur",
    "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur",
    "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar",
    "Kasganj", "Kaushambi", "Kushinagar", "Lakhimpur Kheri",
    "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri",
    "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad",
    "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj",
    "Rae Bareli", "Rampur", "Saharanpur", "Sambhal",
    "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti",
    "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur",
    "Unnao", "Varanasi"
]

LEAD_STATUSES = [
    "New", "Assigned", "Contacted",
    "Site Visit", "Quotation Sent", "Installation",
    "Completed", "Cancelled"
]

# ==========================
# APP CONFIG
# ==========================
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
app.secret_key = os.getenv("SECRET_KEY", "solar_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///solar.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================
# EMAIL FUNCTION
# ==========================
def send_lead_email(lead):
    try:
        msg = EmailMessage()
        msg["Subject"] = "☀ New Solar Lead Received"
        msg["From"] = os.getenv("MAIL_USERNAME")
        msg["To"] = os.getenv("ADMIN_EMAIL")
        msg.set_content(f"""
New Solar Enquiry

Customer Name : {lead.name}
Phone Number  : {lead.phone}
City          : {lead.city}
District      : {lead.district}
Bill Range    : {lead.bill}
Date          : {lead.created_at}
        """)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
            server.send_message(msg)
        print("EMAIL SENT SUCCESSFULLY")
    except Exception as e:
        print("EMAIL ERROR:", e)

# ==========================
# MODELS
# ==========================
class Vendor(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    owner_name   = db.Column(db.String(100), nullable=False)
    mobile       = db.Column(db.String(20), nullable=False)
    email        = db.Column(db.String(150), default="")
    username     = db.Column(db.String(50), unique=True, nullable=False)
    password     = db.Column(db.String(300), nullable=False)
    district     = db.Column(db.String(100), nullable=False)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.String(50), default="")


class Lead(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    phone      = db.Column(db.String(20))
    city       = db.Column(db.String(100))
    bill       = db.Column(db.String(100))
    created_at = db.Column(db.String(50))
    status     = db.Column(db.String(50), default="New")
    note       = db.Column(db.Text, default="")
    follow_date = db.Column(db.String(50), default="")
    updated_by  = db.Column(db.String(100), default="")
    district    = db.Column(db.String(100), default="")
    vendor_id   = db.Column(db.Integer, db.ForeignKey("vendor.id"), nullable=True)
    vendor      = db.relationship("Vendor", backref="leads", foreign_keys=[vendor_id])


class LeadTimeline(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    lead_id    = db.Column(db.Integer, db.ForeignKey("lead.id"), nullable=False)
    event      = db.Column(db.String(200), nullable=False)
    note       = db.Column(db.Text, default="")
    created_by = db.Column(db.String(100), default="")
    created_at = db.Column(db.String(50), default="")
    lead       = db.relationship("Lead", backref="timeline")


class User(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    username   = db.Column(db.String(50), unique=True)
    password   = db.Column(db.String(300))
    role       = db.Column(db.String(50), default="employee")
    created_at = db.Column(db.String(50))

# ==========================
# DB INIT + MIGRATION
# ==========================
with app.app_context():
    db.create_all()

    # Safe migration for existing SQLite database
    db_path = os.path.join("instance", "solar.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(lead)")
        existing = [r[1] for r in cur.fetchall()]
        if "district" not in existing:
            cur.execute("ALTER TABLE lead ADD COLUMN district VARCHAR(100) DEFAULT ''")
        if "vendor_id" not in existing:
            cur.execute("ALTER TABLE lead ADD COLUMN vendor_id INTEGER")
        conn.commit()
        conn.close()

    if not User.query.filter_by(username="admin").first():
        db.session.add(User(
            name="Administrator",
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin",
            created_at=datetime.now().strftime("%d-%m-%Y")
        ))
        db.session.commit()

# ==========================
# HELPERS
# ==========================
def add_timeline(lead_id, event, note="", created_by="Admin"):
    tl = LeadTimeline(
        lead_id=lead_id,
        event=event,
        note=note,
        created_by=created_by,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    db.session.add(tl)
    db.session.commit()

# ==========================
# WEBSITE ROUTES
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

# ==========================
# CONTACT FORM
# ==========================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        lead = Lead(
            name=request.form["name"],
            phone=request.form["phone"],
            city=request.form.get("city", ""),
            district=request.form.get("district", ""),
            bill=request.form["bill"],
            created_at=datetime.now().strftime("%Y-%m-%d"),
            status="New"
        )
        db.session.add(lead)
        db.session.commit()
        add_timeline(lead.id, "Lead Created",
                     f"District: {lead.district}", "Customer")
        send_lead_email(lead)
        return render_template("thankyou.html", name=lead.name, city=lead.city)
    return render_template("contact.html", districts=UP_DISTRICTS)

# ==========================
# ADMIN LOGIN
# ==========================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"]  = user.id
            session["username"] = user.username
            session["role"]     = user.role
            return redirect("/admin")
    return render_template("login.html")

# ==========================
# ADMIN DASHBOARD
# ==========================
@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/admin-login")

    # ── filters ──────────────────────────────────────────────
    f_district = request.args.get("district", "")
    f_vendor   = request.args.get("vendor", "")
    f_status   = request.args.get("status", "")
    f_date     = request.args.get("date", "")
    f_search   = request.args.get("search", "")

    query = Lead.query
    if f_district:
        query = query.filter(Lead.district == f_district)
    if f_vendor:
        query = query.filter(Lead.vendor_id == int(f_vendor))
    if f_status:
        query = query.filter(Lead.status == f_status)
    if f_date:
        query = query.filter(Lead.created_at == f_date)
    if f_search:
        like = f"%{f_search}%"
        query = query.filter(db.or_(
            Lead.name.like(like),
            Lead.phone.like(like),
            Lead.district.like(like)
        ))

    leads   = query.order_by(Lead.id.desc()).all()
    users   = User.query.all()
    vendors = Vendor.query.filter_by(is_active=True).all()

    # ── date helpers ─────────────────────────────────────────
    now       = datetime.now()
    today     = now.strftime("%Y-%m-%d")
    yesterday = (now - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    this_month_prefix = now.strftime("%Y-%m")

    # ── stat card counts ─────────────────────────────────────
    total_leads         = Lead.query.count()
    today_leads_count   = Lead.query.filter(Lead.created_at == today).count()
    yesterday_leads_count = Lead.query.filter(Lead.created_at == yesterday).count()
    this_month_count    = Lead.query.filter(
        Lead.created_at.like(f"{this_month_prefix}%")
    ).count()

    status_counts = {s: Lead.query.filter_by(status=s).count() for s in LEAD_STATUSES}

    pending_statuses    = ["New", "Assigned", "Contacted", "Site Visit", "Quotation Sent", "Installation"]
    pending_leads_count = sum(status_counts[s] for s in pending_statuses)
    assigned_leads_count   = status_counts.get("Assigned", 0)
    completed_leads_count  = status_counts.get("Completed", 0)
    cancelled_leads_count  = status_counts.get("Cancelled", 0)

    total_vendors_count    = Vendor.query.count()
    active_vendors_count   = Vendor.query.filter_by(is_active=True).count()
    inactive_vendors_count = total_vendors_count - active_vendors_count

    # ── follow-ups ───────────────────────────────────────────
    today_followups   = Lead.query.filter_by(follow_date=today).all()
    overdue_followups = Lead.query.filter(
        Lead.follow_date < today,
        Lead.follow_date != "",
        Lead.status.notin_(["Completed", "Cancelled"])
    ).all()

    # ── monthly leads chart — last 12 months ─────────────────
    # group by YYYY-MM (substr positions 1-7 of "YYYY-MM-DD")
    raw_monthly = db.session.query(
        db.func.substr(Lead.created_at, 1, 7).label("ym"),
        db.func.count(Lead.id).label("cnt")
    ).filter(
        Lead.created_at != "",
        Lead.created_at != None
    ).group_by("ym").order_by("ym").all()

    # build a lookup and fill last 12 months with 0 for missing
    monthly_lookup = {row.ym: row.cnt for row in raw_monthly if row.ym}
    month_labels, month_counts = [], []
    for i in range(11, -1, -1):
        import datetime as dt
        d  = now - dt.timedelta(days=i * 30)
        ym = d.strftime("%Y-%m")
        lbl = d.strftime("%b %Y")
        month_labels.append(lbl)
        month_counts.append(monthly_lookup.get(ym, 0))

    # ── status distribution ───────────────────────────────────
    _status_rows = db.session.query(
        Lead.status, db.func.count(Lead.id)
    ).filter(Lead.status != "", Lead.status != None).group_by(Lead.status).all()
    status_data = [{"label": r[0], "count": r[1]} for r in _status_rows]

    # ── top 10 districts ─────────────────────────────────────
    _district_rows = db.session.query(
        Lead.district, db.func.count(Lead.id).label("cnt")
    ).filter(Lead.district != "", Lead.district != None).group_by(Lead.district).order_by(
        db.func.count(Lead.id).desc()
    ).limit(10).all()
    district_data = [{"label": r[0], "count": r[1]} for r in _district_rows]

    # ── vendor performance (top 10) ───────────────────────────
    all_vendors_list = Vendor.query.all()
    vendor_perf = []
    for v in all_vendors_list:
        v_leads     = Lead.query.filter_by(vendor_id=v.id).count()
        if v_leads == 0:
            continue
        v_completed = Lead.query.filter_by(vendor_id=v.id, status="Completed").count()
        v_pending   = v_leads - v_completed
        v_pct       = round((v_completed / v_leads) * 100) if v_leads else 0
        vendor_perf.append({
            "name":      v.company_name,
            "total":     v_leads,
            "completed": v_completed,
            "pending":   v_pending,
            "pct":       v_pct
        })
    vendor_perf.sort(key=lambda x: x["total"], reverse=True)
    vendor_perf = vendor_perf[:10]

    # ── recent leads (latest 10) ──────────────────────────────
    recent_leads = Lead.query.order_by(Lead.id.desc()).limit(10).all()

    # ── recent activities (latest 10 timeline entries) ────────
    recent_activities = LeadTimeline.query.order_by(
        LeadTimeline.id.desc()
    ).limit(10).all()

    return render_template(
        "admin.html",
        leads=leads, users=users, vendors=vendors,
        districts=UP_DISTRICTS, STATUSES=LEAD_STATUSES,
        # stat cards
        status_counts=status_counts,
        total_leads=total_leads,
        today_leads_count=today_leads_count,
        yesterday_leads_count=yesterday_leads_count,
        this_month_count=this_month_count,
        pending_leads_count=pending_leads_count,
        assigned_leads_count=assigned_leads_count,
        completed_leads_count=completed_leads_count,
        cancelled_leads_count=cancelled_leads_count,
        total_vendors_count=total_vendors_count,
        active_vendors_count=active_vendors_count,
        inactive_vendors_count=inactive_vendors_count,
        # charts
        month_labels=month_labels,
        month_counts=month_counts,
        status_data=status_data,
        district_data=district_data,
        vendor_perf=vendor_perf,
        # recent / follow-ups
        recent_leads=recent_leads,
        recent_activities=recent_activities,
        today_followups=today_followups,
        overdue_followups=overdue_followups,
        # filters
        f_district=f_district, f_vendor=f_vendor,
        f_status=f_status, f_date=f_date, f_search=f_search
    )

# ==========================
# ADD EMPLOYEE
# ==========================
@app.route("/add-user", methods=["POST"])
def add_user():
    if session.get("role") != "admin":
        return redirect("/admin")
    user = User(
        name=request.form["name"],
        username=request.form["username"],
        password=generate_password_hash(request.form["password"]),
        role=request.form["role"],
        created_at=datetime.now().strftime("%d-%m-%Y")
    )
    db.session.add(user)
    db.session.commit()
    return redirect("/admin")

# ==========================
# UPDATE STATUS
# ==========================
@app.route("/update-status/<int:id>/<status>")
def update_status(id, status):
    if "user_id" not in session and "vendor_id" not in session:
        return redirect("/admin-login")
    lead = Lead.query.get_or_404(id)
    old_status = lead.status
    lead.status = status
    actor = session.get("username") or session.get("vendor_username", "Vendor")
    lead.updated_by = actor
    db.session.commit()
    add_timeline(lead.id, f"Status Changed: {old_status} → {status}", "", actor)
    if "vendor_id" in session:
        return redirect("/vendor-dashboard")
    return redirect("/admin")

# ==========================
# ADD NOTE / FOLLOW UP
# ==========================
@app.route("/add-note/<int:id>", methods=["POST"])
def add_note(id):
    if "user_id" not in session and "vendor_id" not in session:
        return redirect("/admin-login")
    lead = Lead.query.get_or_404(id)
    new_note = request.form.get("note", "")
    follow_date = request.form.get("follow_date", "")
    lead.note = new_note
    lead.follow_date = follow_date
    actor = session.get("username") or session.get("vendor_username", "Vendor")
    lead.updated_by = actor
    db.session.commit()
    add_timeline(lead.id, "Note Updated", new_note, actor)
    if "vendor_id" in session:
        return redirect("/vendor-dashboard")
    return redirect("/admin")

# ==========================
# DELETE LEAD (admin only)
# ==========================
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return redirect("/admin")
    lead = Lead.query.get_or_404(id)
    LeadTimeline.query.filter_by(lead_id=id).delete()
    db.session.delete(lead)
    db.session.commit()
    return redirect("/admin")

# ==========================
# ASSIGN VENDOR TO LEAD
# ==========================
@app.route("/assign-vendor/<int:lead_id>", methods=["POST"])
def assign_vendor(lead_id):
    if session.get("role") != "admin":
        return redirect("/admin")
    lead = Lead.query.get_or_404(lead_id)
    vendor_id = request.form.get("vendor_id")
    if vendor_id:
        lead.vendor_id = int(vendor_id)
        lead.status = "Assigned"
        lead.updated_by = session.get("username", "Admin")
        db.session.commit()
        vendor = Vendor.query.get(vendor_id)
        v_name = vendor.company_name if vendor else "Unknown"
        add_timeline(lead_id, f"Assigned to Vendor: {v_name}",
                     "", session.get("username", "Admin"))
    return redirect("/admin")

# ==========================
# LEAD TIMELINE API
# ==========================
@app.route("/lead-timeline/<int:lead_id>")
def lead_timeline(lead_id):
    if "user_id" not in session:
        return jsonify([])
    entries = LeadTimeline.query.filter_by(lead_id=lead_id).order_by(
        LeadTimeline.id.asc()
    ).all()
    return jsonify([{
        "event": e.event,
        "note": e.note,
        "created_by": e.created_by,
        "created_at": e.created_at
    } for e in entries])

# ==========================
# VENDOR LOGIN
# ==========================
@app.route("/vendor-login", methods=["GET", "POST"])
def vendor_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        vendor = Vendor.query.filter_by(username=username, is_active=True).first()
        if vendor and check_password_hash(vendor.password, password):
            session["vendor_id"]       = vendor.id
            session["vendor_username"] = vendor.username
            session["vendor_district"] = vendor.district
            session["vendor_company"]  = vendor.company_name
            return redirect("/vendor-dashboard")
        flash("Invalid credentials or inactive account.", "danger")
    return render_template("vendor_login.html")

# ==========================
# VENDOR LOGOUT
# ==========================
@app.route("/vendor-logout")
def vendor_logout():
    session.pop("vendor_id", None)
    session.pop("vendor_username", None)
    session.pop("vendor_district", None)
    session.pop("vendor_company", None)
    return redirect("/vendor-login")

# ==========================
# VENDOR DASHBOARD
# ==========================
@app.route("/vendor-dashboard")
def vendor_dashboard():
    if "vendor_id" not in session:
        return redirect("/vendor-login")

    vendor_id = session["vendor_id"]
    vendor    = Vendor.query.get_or_404(vendor_id)

    f_status = request.args.get("status", "")
    f_search = request.args.get("search", "")

    query = Lead.query.filter_by(vendor_id=vendor_id)
    if f_status:
        query = query.filter(Lead.status == f_status)
    if f_search:
        like = f"%{f_search}%"
        query = query.filter(db.or_(
            Lead.name.like(like), Lead.phone.like(like)
        ))

    leads = query.order_by(Lead.id.desc()).all()

    total_leads     = Lead.query.filter_by(vendor_id=vendor_id).count()
    completed_leads = Lead.query.filter_by(vendor_id=vendor_id, status="Completed").count()
    pending_leads   = Lead.query.filter(
        Lead.vendor_id == vendor_id,
        Lead.status.notin_(["Completed", "Cancelled"])
    ).count()
    cancelled_leads = Lead.query.filter_by(vendor_id=vendor_id, status="Cancelled").count()
    completion_pct  = round((completed_leads / total_leads * 100), 1) if total_leads else 0

    today = datetime.now().strftime("%Y-%m-%d")
    today_followups = Lead.query.filter_by(
        vendor_id=vendor_id, follow_date=today
    ).all()

    return render_template(
        "vendor_dashboard.html",
        vendor=vendor,
        leads=leads,
        STATUSES=LEAD_STATUSES,
        total_leads=total_leads,
        completed_leads=completed_leads,
        pending_leads=pending_leads,
        cancelled_leads=cancelled_leads,
        completion_pct=completion_pct,
        today_followups=today_followups,
        f_status=f_status,
        f_search=f_search
    )

# ==========================
# VENDOR LIST (admin)
# ==========================
@app.route("/vendors")
def vendor_list():
    if "user_id" not in session:
        return redirect("/admin-login")
    f_district = request.args.get("district", "")
    f_active   = request.args.get("active", "")
    query = Vendor.query
    if f_district:
        query = query.filter(Vendor.district == f_district)
    if f_active != "":
        query = query.filter(Vendor.is_active == (f_active == "1"))
    vendors = query.order_by(Vendor.id.desc()).all()

    # Performance stats per vendor
    perf = {}
    for v in vendors:
        total     = Lead.query.filter_by(vendor_id=v.id).count()
        completed = Lead.query.filter_by(vendor_id=v.id, status="Completed").count()
        pending   = Lead.query.filter(
            Lead.vendor_id == v.id,
            Lead.status.notin_(["Completed", "Cancelled"])
        ).count()
        cancelled = Lead.query.filter_by(vendor_id=v.id, status="Cancelled").count()
        pct       = round((completed / total * 100), 1) if total else 0
        perf[v.id] = {
            "total": total, "completed": completed,
            "pending": pending, "cancelled": cancelled, "pct": pct
        }

    return render_template(
        "vendor_list.html",
        vendors=vendors, perf=perf,
        districts=UP_DISTRICTS,
        f_district=f_district, f_active=f_active
    )

# ==========================
# ADD VENDOR (admin)
# ==========================
@app.route("/vendor-add", methods=["GET", "POST"])
def vendor_add():
    if "user_id" not in session:
        return redirect("/admin-login")
    if request.method == "POST":
        existing = Vendor.query.filter_by(
            username=request.form["username"]
        ).first()
        if existing:
            flash("Username already exists.", "danger")
            return render_template("vendor_add.html", districts=UP_DISTRICTS)
        vendor = Vendor(
            company_name=request.form["company_name"],
            owner_name=request.form["owner_name"],
            mobile=request.form["mobile"],
            email=request.form.get("email", ""),
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            district=request.form["district"],
            is_active=True,
            created_at=datetime.now().strftime("%d-%m-%Y")
        )
        db.session.add(vendor)
        db.session.commit()
        flash("Vendor added successfully.", "success")
        return redirect("/vendors")
    return render_template("vendor_add.html", districts=UP_DISTRICTS)

# ==========================
# EDIT VENDOR (admin)
# ==========================
@app.route("/vendor-edit/<int:vendor_id>", methods=["GET", "POST"])
def vendor_edit(vendor_id):
    if "user_id" not in session:
        return redirect("/admin-login")
    vendor = Vendor.query.get_or_404(vendor_id)
    if request.method == "POST":
        vendor.company_name = request.form["company_name"]
        vendor.owner_name   = request.form["owner_name"]
        vendor.mobile       = request.form["mobile"]
        vendor.email        = request.form.get("email", "")
        vendor.district     = request.form["district"]
        vendor.is_active    = request.form.get("is_active") == "1"
        new_pass = request.form.get("password", "").strip()
        if new_pass:
            vendor.password = generate_password_hash(new_pass)
        db.session.commit()
        flash("Vendor updated successfully.", "success")
        return redirect("/vendors")
    return render_template("vendor_edit.html", vendor=vendor, districts=UP_DISTRICTS)

# ==========================
# DELETE VENDOR (admin)
# ==========================
@app.route("/vendor-delete/<int:vendor_id>")
def vendor_delete(vendor_id):
    if session.get("role") != "admin":
        return redirect("/vendors")
    vendor = Vendor.query.get_or_404(vendor_id)
    # Unassign leads
    Lead.query.filter_by(vendor_id=vendor_id).update(
        {"vendor_id": None, "status": "New"}
    )
    db.session.delete(vendor)
    db.session.commit()
    flash("Vendor deleted.", "success")
    return redirect("/vendors")

# ==========================
# TOGGLE VENDOR STATUS
# ==========================
@app.route("/vendor-toggle/<int:vendor_id>")
def vendor_toggle(vendor_id):
    if session.get("role") != "admin":
        return redirect("/vendors")
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.is_active = not vendor.is_active
    db.session.commit()
    return redirect("/vendors")

# ==========================
# IMPORT VENDORS FROM EXCEL
# ==========================
@app.route("/import-vendors", methods=["GET", "POST"])
def import_vendors():
    if session.get("role") != "admin":
        return redirect("/admin")
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file selected.", "danger")
            return redirect("/import-vendors")
        try:
            df = pd.read_excel(file)
            # Normalize column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            required = {"company_name", "owner_name", "mobile", "district"}
            if not required.issubset(set(df.columns)):
                flash(f"Excel must have columns: {', '.join(required)}", "danger")
                return redirect("/import-vendors")
            added = 0
            skipped = 0
            for _, row in df.iterrows():
                company  = str(row.get("company_name", "")).strip()
                owner    = str(row.get("owner_name", "")).strip()
                mobile   = str(row.get("mobile", "")).strip()
                district = str(row.get("district", "")).strip()
                email    = str(row.get("email", "")).strip()
                if not company or not mobile:
                    skipped += 1
                    continue
                # Auto-generate username from mobile
                username = f"vendor_{mobile}"
                if Vendor.query.filter_by(username=username).first():
                    skipped += 1
                    continue
                vendor = Vendor(
                    company_name=company,
                    owner_name=owner,
                    mobile=mobile,
                    email=email,
                    username=username,
                    password=generate_password_hash(mobile),
                    district=district,
                    is_active=True,
                    created_at=datetime.now().strftime("%d-%m-%Y")
                )
                db.session.add(vendor)
                added += 1
            db.session.commit()
            flash(f"Import complete: {added} added, {skipped} skipped.", "success")
        except Exception as e:
            flash(f"Import failed: {str(e)}", "danger")
        return redirect("/vendors")
    return render_template("import_vendors.html")

# ==========================
# PROFESSIONAL EXCEL EXPORT
# ==========================
@app.route("/download-leads")
def download():
    if "user_id" not in session:
        return redirect("/admin-login")

    leads = Lead.query.order_by(Lead.id.desc()).all()

    data = []
    for lead in leads:
        data.append({
            "ID": lead.id,
            "Customer Name": lead.name,
            "Mobile Number": lead.phone,
            "City": lead.city,
            "District": lead.district,
            "Monthly Bill": lead.bill,
            "Status": lead.status,
            "Assigned Vendor": lead.vendor.company_name if lead.vendor else "",
            "Follow Note": lead.note,
            "Follow Date": lead.follow_date,
            "Updated By": lead.updated_by,
            "Created Date": lead.created_at
        })

    filename = "Har_Ghar_Solar_CRM.xlsx"
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, startrow=5)

    wb = load_workbook(filename)
    ws = wb.active
    ws.title = "Solar Leads"

    # Branding header
    num_cols = len(data[0]) if data else 12
    last_col = get_column_letter(num_cols)

    ws.merge_cells(f"A1:{last_col}1")
    ws["A1"] = "HAR GHAR SOLAR — CRM Report"
    ws["A1"].font      = Font(bold=True, size=20, color="FFFFFF")
    ws["A1"].fill      = PatternFill("solid", fgColor="005B38")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 35

    ws.merge_cells(f"A2:{last_col}2")
    ws["A2"] = f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}  |  Total Leads: {len(leads)}"
    ws["A2"].font      = Font(size=11, color="FFFFFF")
    ws["A2"].fill      = PatternFill("solid", fgColor="007A3D")
    ws["A2"].alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 22

    # Status summary
    ws.merge_cells(f"A3:{last_col}3")
    summary = "  |  ".join([f"{s}: {Lead.query.filter_by(status=s).count()}" for s in LEAD_STATUSES])
    ws["A3"] = summary
    ws["A3"].font      = Font(size=10, bold=True, color="005B38")
    ws["A3"].fill      = PatternFill("solid", fgColor="E8F5E9")
    ws["A3"].alignment = Alignment(horizontal="center")

    ws.merge_cells(f"A4:{last_col}4")
    ws["A4"] = ""

    # Header row style
    status_col_idx = None
    for i, cell in enumerate(ws[6], 1):
        cell.font      = Font(bold=True, color="FFFFFF", size=11)
        cell.fill      = PatternFill("solid", fgColor="1B5E20")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        if cell.value == "Status":
            status_col_idx = i
    ws.row_dimensions[6].height = 24

    # Status color map
    status_colors = {
        "New":           "FFF9C4",
        "Assigned":      "E3F2FD",
        "Contacted":     "E8EAF6",
        "Site Visit":    "F3E5F5",
        "Quotation Sent":"FFF3E0",
        "Installation":  "E0F2F1",
        "Completed":     "C8E6C9",
        "Cancelled":     "FFCDD2"
    }

    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    for row in ws.iter_rows(min_row=6):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if cell.row % 2 == 0 and cell.row > 6:
                if not (status_col_idx and cell.column == status_col_idx):
                    cell.fill = PatternFill("solid", fgColor="F1F8F4")

    # Status badge coloring
    if status_col_idx:
        for row in ws.iter_rows(min_row=7, min_col=status_col_idx, max_col=status_col_idx):
            for cell in row:
                val = str(cell.value) if cell.value else ""
                if val in status_colors:
                    cell.fill = PatternFill("solid", fgColor=status_colors[val])
                    cell.font = Font(bold=True, size=10)

    # Column widths
    col_widths = {
        "A": 6, "B": 22, "C": 15, "D": 15, "E": 18,
        "F": 18, "G": 16, "H": 24, "I": 28, "J": 14,
        "K": 16, "L": 14
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width
    ws.row_dimensions[6].height = 24
    for r in range(7, ws.max_row + 1):
        ws.row_dimensions[r].height = 18

    # Excel table
    try:
        last_row    = ws.max_row
        table_range = f"A6:{last_col}{last_row}"
        tbl = Table(displayName="SolarLeads", ref=table_range)
        tbl.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium7",
            showFirstColumn=False, showLastColumn=False,
            showRowStripes=True, showColumnStripes=False
        )
        ws.add_table(tbl)
    except Exception as e:
        print("TABLE ERROR:", e)

    ws.freeze_panes = "A7"
    wb.save(filename)

    return send_file(filename, as_attachment=True, download_name=filename)


# ==========================
# LEAD DETAIL API (JSON)
# ==========================
@app.route("/lead-detail/<int:lead_id>")
def lead_detail(lead_id):
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401
    lead = Lead.query.get_or_404(lead_id)
    return jsonify({
        "id":          lead.id,
        "name":        lead.name or "",
        "phone":       lead.phone or "",
        "city":        lead.city or "",
        "district":    lead.district or "",
        "bill":        lead.bill or "",
        "status":      lead.status or "New",
        "note":        lead.note or "",
        "follow_date": lead.follow_date or "",
        "updated_by":  lead.updated_by or "",
        "created_at":  lead.created_at or "",
        "vendor_id":   lead.vendor_id or "",
        "vendor_name": lead.vendor.company_name if lead.vendor else ""
    })

# ==========================
# LEAD EDIT (POST — saves edits)
# ==========================
@app.route("/lead-edit/<int:lead_id>", methods=["POST"])
def lead_edit(lead_id):
    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401
    lead = Lead.query.get_or_404(lead_id)
    old_status = lead.status
    lead.name        = request.form.get("name",        lead.name)
    lead.phone       = request.form.get("phone",       lead.phone)
    lead.city        = request.form.get("city",        lead.city)
    lead.district    = request.form.get("district",    lead.district)
    lead.bill        = request.form.get("bill",        lead.bill)
    lead.status      = request.form.get("status",      lead.status)
    lead.note        = request.form.get("note",        lead.note)
    lead.follow_date = request.form.get("follow_date", lead.follow_date)
    new_vendor_id    = request.form.get("vendor_id",   "")
    lead.vendor_id   = int(new_vendor_id) if new_vendor_id else None
    actor            = session.get("username", "Admin")
    lead.updated_by  = actor
    db.session.commit()
    if lead.status != old_status:
        add_timeline(lead.id, f"Status Changed: {old_status} → {lead.status}", "", actor)
    add_timeline(lead.id, "Lead Updated via Edit", "", actor)
    return jsonify({"success": True, "message": "Lead updated successfully."})

# ==========================
# LOGOUT (Admin)
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin-login")

# ==========================
# AZURE UPLOAD ROUTE
# ==========================
from azure_storage import upload_file

@app.route("/azure-upload", methods=["GET", "POST"])
def azure_upload():
    if request.method == "POST":
        file = request.files["file"]
        url  = upload_file(file)
        return f'Upload Successful<br><br>URL: <a href="{url}" target="_blank">{url}</a>'
    return """
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <button>Upload</button>
    </form>
    """

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)
