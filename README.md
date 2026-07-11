# ☀️ Har Ghar Solar — CRM & Website

Production-ready Flask CRM for a rooftop solar installation company in Uttar Pradesh, India. Supports PM Surya Ghar Yojana subsidy workflows, full lead management, vendor assignment, and a premium public-facing website.

---

## 🚀 Features

### Public Website
- Premium responsive landing page with hero carousel
- PM Surya Ghar government subsidy information
- Solar savings calculator
- Project gallery with lightbox
- Customer reviews
- SEO: meta tags, Open Graph, Schema.org, sitemap.xml, robots.txt
- Persistent visitor counter
- Clickable phone / WhatsApp / email links
- Embedded Google Maps

### CRM — Admin Panel
- Secure login with brute-force rate limiting
- Full lead management: search, filter by district/status/vendor/date, pagination
- Lead timeline & follow-up scheduling
- Vendor assignment per lead
- User management: create / disable / reset password / delete admin users
- Professional Excel export with company branding & colour-coded status
- Dashboard: 12-month chart, status distribution, district heatmap, vendor performance

### Vendor Portal
- Vendor login & dashboard
- View assigned leads, update status, add notes

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask 3.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 |
| Frontend | Bootstrap 5.3, Poppins font, Font Awesome 6 |
| Animations | AOS 2.3 |
| Excel | openpyxl, pandas |
| Server | Gunicorn + Nginx (production) |

---

## ⚡ Quick Start (Local)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_ORG/har-ghar-solar.git
cd har-ghar-solar

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your SECRET_KEY and optional email settings

# 5. Run development server
python app.py
# App available at http://localhost:5000
```

**Default admin credentials:** `admin` / `admin123`  
⚠️ Change immediately after first login.

---

## 🌐 Production Deployment

See [deployment.md](deployment.md) for the complete AWS EC2 + Ubuntu + Gunicorn + Nginx + Systemd guide.

---

## 📁 Project Structure

```
har-ghar-solar/
├── app.py                  # Main Flask application
├── azure_storage.py        # Local file upload helper
├── wsgi.py                 # WSGI entry point for Gunicorn
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku/platform process file
├── runtime.txt             # Python version pin
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
├── deployment.md           # AWS deployment guide
├── static/
│   ├── css/
│   │   ├── style.css       # Main premium theme
│   │   ├── responsive.css  # All breakpoints
│   │   ├── variables.css   # CSS custom properties
│   │   └── admin.css       # Admin panel styles
│   ├── js/
│   │   ├── main.js         # Public site JS
│   │   └── admin.js        # Admin panel JS
│   ├── images/             # Logo, hero, project photos
│   ├── robots.txt
│   └── sitemap.xml
└── templates/
    ├── base.html           # Public base layout
    ├── admin_base.html     # Admin base layout
    ├── index.html
    ├── about.html
    ├── services.html
    ├── contact.html
    ├── thankyou.html
    ├── login.html
    ├── admin.html
    ├── vendor_*.html
    ├── partials/           # Reusable template fragments
    └── errors/             # 400, 403, 404, 429, 500
```

---

## 🔒 Security Notes

- `SECRET_KEY` must be a strong random value in production
- Admin panel protected with session auth + rate limiting (10 req/min)
- All admin routes require authentication via `@login_required` decorator
- Destructive actions (delete user/vendor/lead) require `@admin_required`
- `SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE=Lax`
- `.env` is listed in `.gitignore` — never commit secrets

---

## 📧 Email Notifications

Set in `.env`:
```
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=gmail-app-password   # Use App Password, not account password
ADMIN_EMAIL=admin@hargharsolar.in
```
Leave blank to disable email notifications silently.

---

## 📄 License

MIT License — © 2026 Har Ghar Solar
