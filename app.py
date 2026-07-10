from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from openpyxl.utils import get_column_letter
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime

import pandas as pd

import os

from openpyxl.worksheet.table import (
    Table,
    TableStyleInfo
)

from dotenv import load_dotenv


# EMAIL
import smtplib

from email.message import EmailMessage



# EXCEL STYLE

from openpyxl import load_workbook

from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)



# ==========================
# APP CONFIG
# ==========================


load_dotenv()


app = Flask(__name__)


app.secret_key = os.getenv(
    "SECRET_KEY",
    "solar_secret_key"
)



app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///solar.db"
)


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)





# ==========================
# EMAIL FUNCTION
# ==========================


def send_lead_email(lead):


    try:


        msg = EmailMessage()


        msg["Subject"] = "☀ New Solar Lead Received"


        msg["From"] = os.getenv(
            "MAIL_USERNAME"
        )


        msg["To"] = os.getenv(
            "ADMIN_EMAIL"
        )



        msg.set_content(
            f"""

New Solar Enquiry


Customer Name : {lead.name}

Phone Number  : {lead.phone}

City          : {lead.city}

Bill Range    : {lead.bill}

Date          : {lead.created_at}


            """
        )




        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:


            server.starttls()



            server.login(

                os.getenv(
                    "MAIL_USERNAME"
                ),


                os.getenv(
                    "MAIL_PASSWORD"
                )

            )



            server.send_message(msg)



        print("EMAIL SENT SUCCESSFULLY")




    except Exception as e:


        print(
            "EMAIL ERROR:",
            e
        )







# ==========================
# LEAD MODEL
# ==========================


class Lead(db.Model):


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(100)
    )


    phone = db.Column(
        db.String(20)
    )


    city = db.Column(
        db.String(100)
    )


    bill = db.Column(
        db.String(100)
    )


    created_at = db.Column(
        db.String(50)
    )


    status = db.Column(
        db.String(50),
        default="New"
    )


    note = db.Column(
        db.Text,
        default=""
    )


    follow_date = db.Column(
        db.String(50),
        default=""
    )


    updated_by = db.Column(
        db.String(100),
        default=""
    )








# ==========================
# USER MODEL
# ==========================


class User(db.Model):


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(100)
    )


    username = db.Column(
        db.String(50),
        unique=True
    )


    password = db.Column(
        db.String(300)
    )


    role = db.Column(
        db.String(50),
        default="employee"
    )


    created_at = db.Column(
        db.String(50)
    )






# ==========================
# CREATE TABLES + ADMIN
# ==========================


with app.app_context():


    db.create_all()



    admin = User.query.filter_by(
        username="admin"
    ).first()



    if not admin:


        admin = User(

            name="Administrator",

            username="admin",

            password=generate_password_hash(
                "admin123"
            ),

            role="admin",

            created_at=datetime.now().strftime(
                "%d-%m-%Y"
            )

        )



        db.session.add(admin)

        db.session.commit()

# ==========================
# WEBSITE ROUTES
# ==========================


@app.route("/")
def home():

    return render_template(
        "index.html"
    )



@app.route("/about")
def about():

    return render_template(
        "about.html"
    )



@app.route("/services")
def services():

    return render_template(
        "services.html"
    )






# ==========================
# CONTACT FORM + EMAIL
# ==========================


@app.route(
    "/contact",
    methods=["GET","POST"]
)


def contact():


    if request.method == "POST":


        lead = Lead(

            name=request.form["name"],

            phone=request.form["phone"],

            city=request.form["city"],

            bill=request.form["bill"],


            created_at=datetime.now().strftime(
                "%Y-%m-%d"
            ),


            status="New"

        )



        db.session.add(lead)


        db.session.commit()



        # SEND EMAIL

        send_lead_email(
            lead
        )



        return render_template(

            "thankyou.html",

            name=lead.name,

            city=lead.city

        )



    return render_template(
        "contact.html"
    )









# ==========================
# LOGIN SYSTEM
# ==========================


@app.route(
    "/admin-login",
    methods=["GET","POST"]
)


def admin_login():


    if request.method=="POST":



        username=request.form["username"]

        password=request.form["password"]




        user=User.query.filter_by(

            username=username

        ).first()






        if user and check_password_hash(

            user.password,

            password

        ):



            session["user_id"]=user.id

            session["username"]=user.username

            session["role"]=user.role




            return redirect(
                "/admin"
            )



    return render_template(
        "login.html"
    )










# ==========================
# ADMIN DASHBOARD
# ==========================


@app.route("/admin")


def admin():


    if "user_id" not in session:


        return redirect(
            "/admin-login"
        )






    leads = Lead.query.order_by(

        Lead.id.desc()

    ).all()



    today = datetime.now().strftime(

        "%Y-%m-%d"

    )



    today_followups = Lead.query.filter_by(

        follow_date=today

    ).all()

    overdue_followups = Lead.query.filter(

        Lead.follow_date < today,

        Lead.follow_date != "",

        Lead.status != "Installed"

    ).all()
    
    users = User.query.all()



    new_count = Lead.query.filter_by(

        status="New"

    ).count()



    contacted_count = Lead.query.filter_by(

        status="Contacted"

    ).count()



    installed_count = Lead.query.filter_by(

        status="Installed"

    ).count()



    chart_data = db.session.query(


        db.func.substr(

            Lead.created_at,

            6,

            2

        ),


        db.func.count(

            Lead.id

        )


    ).group_by(


        db.func.substr(

            Lead.created_at,

            6,

            2

        )


    ).all()





    return render_template(

        "admin.html",

        leads=leads,

        users=users,

        new_count=new_count,

        contacted_count=contacted_count,

        installed_count=installed_count,

        chart_data=chart_data,

        today_followups=today_followups,

        overdue_followups=overdue_followups

    )   

# ==========================
# ADD EMPLOYEE
# ==========================


@app.route(
    "/add-user",
    methods=["POST"]
)


def add_user():



    if session.get("role")!="admin":


        return redirect(
            "/admin"
        )






    user=User(


        name=request.form["name"],


        username=request.form["username"],


        password=generate_password_hash(

            request.form["password"]

        ),



        role=request.form["role"],



        created_at=datetime.now().strftime(

            "%d-%m-%Y"

        )

    )





    db.session.add(user)


    db.session.commit()




    return redirect(
        "/admin"
    )
# ==========================
# UPDATE STATUS
# ==========================


@app.route("/update-status/<int:id>/<status>")

def update_status(id,status):


    if "user_id" not in session:

        return redirect("/admin-login")



    lead = Lead.query.get_or_404(id)



    lead.status = status



    lead.updated_by = session.get(
        "username"
    )



    db.session.commit()



    return redirect("/admin")









# ==========================
# FOLLOW UP NOTE
# ==========================


@app.route("/add-note/<int:id>", methods=["POST"])


def add_note(id):


    if "user_id" not in session:

        return redirect("/admin-login")



    lead = Lead.query.get_or_404(id)



    lead.note = request.form.get(
        "note"
    )



    lead.follow_date = request.form.get(
        "follow_date"
    )



    lead.updated_by = session.get(
        "username"
    )



    db.session.commit()



    return redirect("/admin")










# ==========================
# DELETE LEAD
# ADMIN ONLY
# ==========================


@app.route("/delete/<int:id>")


def delete(id):


    if session.get("role") != "admin":

        return redirect("/admin")



    lead = Lead.query.get_or_404(id)



    db.session.delete(lead)



    db.session.commit()



    return redirect("/admin")










# ==========================
# PROFESSIONAL EXCEL EXPORT
# ==========================


@app.route("/download-leads")
def download():


    if "user_id" not in session:

        return redirect("/admin-login")



    leads = Lead.query.order_by(
        Lead.id.desc()
    ).all()



    data = []


    for lead in leads:


        data.append({

            "ID": lead.id,

            "Customer Name": lead.name,

            "Mobile Number": lead.phone,

            "City": lead.city,

            "Monthly Bill": lead.bill,

            "Status": lead.status,

            "Follow Note": lead.note,

            "Follow Date": lead.follow_date,

            "Updated By": lead.updated_by,

            "Created Date": lead.created_at

        })




    filename = "Har_Ghar_Solar_CRM.xlsx"



    df = pd.DataFrame(data)


    df.to_excel(

        filename,

        index=False,

        startrow=3

    )





    wb = load_workbook(filename)


    ws = wb.active


    ws.title = "Solar Leads"




    # =====================
    # TITLE
    # =====================


    ws.merge_cells("A1:J1")


    ws["A1"] = "☀ Har Ghar Solar CRM Report"


    ws["A1"].font = Font(

        bold=True,

        size=18,

        color="FFFFFF"

    )


    ws["A1"].fill = PatternFill(

        "solid",

        fgColor="007A3D"

    )


    ws["A1"].alignment = Alignment(

        horizontal="center"

    )





    # =====================
    # HEADER STYLE
    # =====================


    for cell in ws[4]:


        cell.font = Font(

            bold=True,

            color="FFFFFF"

        )


        cell.fill = PatternFill(

            "solid",

            fgColor="008000"

        )


        cell.alignment = Alignment(

            horizontal="center"

        )





    # =====================
    # BORDER
    # =====================


    border = Border(

        left=Side(style="thin"),

        right=Side(style="thin"),

        top=Side(style="thin"),

        bottom=Side(style="thin")

    )


    for row in ws.iter_rows():


        for cell in row:


            cell.border = border








# =====================
# COLUMN WIDTH FIX
# =====================

    for col in range(1, ws.max_column + 1):

        letter = get_column_letter(col)

        # ID column fixed
        if letter == "A":
            ws.column_dimensions[letter].width = 8
            continue

    max_length = 0

    for row in range(4, ws.max_row + 1):   # header row (4) se start

        value = ws.cell(row=row, column=col).value

        if value is not None:
            max_length = max(max_length, len(str(value)))

    ws.column_dimensions[letter].width = max_length + 5







    # =====================
    # EXCEL TABLE FILTER
    # =====================


    try:


        last_row = ws.max_row


        table_range = f"A4:J{last_row}"


        excel_table = Table(

            displayName="SolarLeads",

            ref=table_range

        )


        style = TableStyleInfo(

            name="TableStyleMedium4",

            showFirstColumn=False,

            showLastColumn=False,

            showRowStripes=True,

            showColumnStripes=False

        )


        excel_table.tableStyleInfo = style


        ws.add_table(excel_table)



    except Exception as e:


        print("TABLE ERROR:", e)






    ws.freeze_panes = "A5"



    wb.save(filename)





    return send_file(

        filename,

        as_attachment=True,

        download_name=filename

    )



    # =====================
    # REAL EXCEL TABLE
    # =====================

    last_row = ws.max_row


    table_range = f"A4:J{last_row}"


    excel_table = Table(

        displayName="SolarLeadsTable",

        ref=table_range

    )


    style = TableStyleInfo(

        name="TableStyleMedium4",

        showFirstColumn=False,

        showLastColumn=False,

        showRowStripes=True,

        showColumnStripes=False

    )


    excel_table.tableStyleInfo = style


    ws.add_table(excel_table)



    ws.freeze_panes = "A5"



    wb.save(filename)



    return send_file(

        filename,

        as_attachment=True,

        download_name="Har_Ghar_Solar_CRM.xlsx"

    )


# ==========================
# LOGOUT
# ==========================


@app.route("/logout")


def logout():


    session.clear()


    return redirect("/admin-login")









# ==========================
# RUN SERVER
# ==========================


if __name__=="__main__":


    port=int(

        os.environ.get(

            "PORT",

            5002

        )

    )




    app.run(

        host="0.0.0.0",

        port=port

    )