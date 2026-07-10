from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv


# ==========================
# APP CONFIG
# ==========================

load_dotenv()


app = Flask(__name__)


app.secret_key = os.getenv(
    "SECRET_KEY",
    "default_secret_key"
)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///solar.db"
)


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)





# ==========================
# DATABASE MODEL
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





with app.app_context():

    db.create_all()







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


@app.route("/contact", methods=["GET","POST"])

def contact():


    if request.method == "POST":


        lead = Lead(

            name=request.form["name"],

            phone=request.form["phone"],

            city=request.form["city"],

            bill=request.form["bill"],

            created_at=datetime.now().strftime("%Y-%m-%d"),

            status="New"

        )



        db.session.add(lead)

        db.session.commit()



        return render_template(
            "thankyou.html",
            name=lead.name,
            city=lead.city
        )



    return render_template("contact.html")










# ==========================
# ADMIN LOGIN
# ==========================


@app.route("/admin-login", methods=["GET","POST"])

def admin_login():


    if request.method=="POST":


        username=request.form["username"]

        password=request.form["password"]



        if (

            username == os.getenv("ADMIN_USERNAME")

            and

            password == os.getenv("ADMIN_PASSWORD")

        ):


            session["admin"] = True


            return redirect("/admin")




    return render_template("login.html")










# ==========================
# ADMIN DASHBOARD
# ==========================


@app.route("/admin")

def admin():


    if "admin" not in session:

        return redirect("/admin-login")



    leads = Lead.query.order_by(
        Lead.id.desc()
    ).all()



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

        new_count=new_count,

        contacted_count=contacted_count,

        installed_count=installed_count,

        chart_data=chart_data

    )









# ==========================
# UPDATE STATUS
# ==========================


@app.route("/update-status/<int:id>/<status>")


def update_status(id,status):


    if "admin" not in session:

        return redirect("/admin-login")



    lead = Lead.query.get_or_404(id)


    lead.status = status


    db.session.commit()



    return redirect("/admin")









# ==========================
# FOLLOW UP NOTES
# ==========================


@app.route("/add-note/<int:id>", methods=["POST"])


def add_note(id):


    if "admin" not in session:

        return redirect("/admin-login")



    lead = Lead.query.get_or_404(id)



    lead.note = request.form.get("note")


    lead.follow_date = request.form.get(
        "follow_date"
    )



    db.session.commit()



    return redirect("/admin")









# ==========================
# DELETE LEAD
# ==========================


@app.route("/delete/<int:id>")


def delete(id):


    if "admin" not in session:

        return redirect("/admin-login")



    lead = Lead.query.get_or_404(id)


    db.session.delete(lead)


    db.session.commit()



    return redirect("/admin")










# ==========================
# EXPORT EXCEL
# ==========================


@app.route("/download-leads")


def download():


    if "admin" not in session:

        return redirect("/admin-login")



    leads = Lead.query.all()



    data=[]



    for lead in leads:


        data.append({

            "ID": lead.id,

            "Name": lead.name,

            "Phone": lead.phone,

            "City": lead.city,

            "Bill": lead.bill,

            "Status": lead.status,

            "Note": lead.note,

            "Follow Date": lead.follow_date,

            "Created": lead.created_at

        })





    df = pd.DataFrame(data)


    file = "Har_Ghar_Solar_Leads.xlsx"


    df.to_excel(

        file,

        index=False

    )



    return send_file(

        file,

        as_attachment=True

    )









# ==========================
# LOGOUT
# ==========================


@app.route("/logout")

def logout():


    session.clear()


    return redirect("/admin-login")










# ==========================
# RUN
# ==========================


if __name__=="__main__":


    port = int(

        os.environ.get(

            "PORT",

            5002

        )

    )



    app.run(

        host="0.0.0.0",

        port=port

    )