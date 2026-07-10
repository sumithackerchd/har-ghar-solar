from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook
import os



app = Flask(__name__)

app.secret_key = "har_ghar_solar_secret"



# ==========================
# DATABASE
# ==========================


def create_database():


    conn = sqlite3.connect("solar.db")

    cur = conn.cursor()



    cur.execute("""
    
    CREATE TABLE IF NOT EXISTS leads(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        phone TEXT,

        city TEXT,

        bill TEXT,

        created_at TEXT,

        status TEXT DEFAULT 'New',

        note TEXT DEFAULT '',

        follow_date TEXT DEFAULT ''

    )

    """)



    conn.commit()

    conn.close()



create_database()







# ==========================
# WEBSITE PAGES
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


    if request.method=="POST":


        name=request.form["name"]

        phone=request.form["phone"]

        city=request.form["city"]

        bill=request.form["bill"]


        date=datetime.now().strftime("%Y-%m-%d")



        conn=sqlite3.connect("solar.db")

        cur=conn.cursor()



        cur.execute(

        """

        INSERT INTO leads(

        name,

        phone,

        city,

        bill,

        created_at,

        status

        )

        VALUES(?,?,?,?,?,?)

        """,

        (

        name,

        phone,

        city,

        bill,

        date,

        "New"

        )

        )



        conn.commit()

        conn.close()



        return render_template(

            "thankyou.html",

            name=name,

            city=city

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



        if username=="admin" and password=="Solar@2026":


            session["admin"]=True


            return redirect("/admin")




    return render_template("login.html")










# ==========================
# ADMIN DASHBOARD
# ==========================


@app.route("/admin")

def admin():


    if "admin" not in session:


        return redirect("/admin-login")




    conn=sqlite3.connect("solar.db")

    cur=conn.cursor()




    cur.execute("""
    
    SELECT

    id,

    name,

    phone,

    city,

    bill,

    created_at,

    status,

    note,

    follow_date

    FROM leads

    ORDER BY id DESC
    
    """)



    leads=cur.fetchall()







    cur.execute(

    "SELECT COUNT(*) FROM leads WHERE status='New'"

    )

    new_count=cur.fetchone()[0]





    cur.execute(

    "SELECT COUNT(*) FROM leads WHERE status='Contacted'"

    )

    contacted_count=cur.fetchone()[0]






    cur.execute(

    "SELECT COUNT(*) FROM leads WHERE status='Installed'"

    )

    installed_count=cur.fetchone()[0]






    # CHART DATA

    cur.execute("""
    
    SELECT

    strftime('%m',created_at),

    COUNT(*)

    FROM leads

    GROUP BY strftime('%m',created_at)

    """)


    chart_data=cur.fetchall()




    conn.close()





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



    conn=sqlite3.connect("solar.db")

    cur=conn.cursor()



    cur.execute(

    "UPDATE leads SET status=? WHERE id=?",

    (status,id)

    )



    conn.commit()

    conn.close()



    return redirect("/admin")









# ==========================
# NOTES + FOLLOW DATE
# ==========================



@app.route("/add-note/<int:id>", methods=["POST"])


def add_note(id):


    if "admin" not in session:


        return redirect("/admin-login")




    note=request.form.get("note")


    follow_date=request.form.get("follow_date")





    conn=sqlite3.connect("solar.db")

    cur=conn.cursor()




    cur.execute(

    """

    UPDATE leads

    SET note=?,

    follow_date=?

    WHERE id=?

    """,

    (

    note,

    follow_date,

    id

    )

    )



    conn.commit()


    conn.close()




    return redirect("/admin")









# ==========================
# DELETE LEAD
# ==========================


@app.route("/delete/<int:id>")


def delete(id):


    if "admin" not in session:

        return redirect("/admin-login")



    conn=sqlite3.connect("solar.db")

    cur=conn.cursor()



    cur.execute(

    "DELETE FROM leads WHERE id=?",

    (id,)

    )



    conn.commit()

    conn.close()



    return redirect("/admin")









# ==========================
# EXCEL EXPORT
# ==========================


@app.route("/download-leads")


def download():


    if "admin" not in session:

        return redirect("/admin-login")



    conn = sqlite3.connect("solar.db")


    df = pd.read_sql_query(
        
        """

        SELECT 

        id as ID,

        name as Customer_Name,

        phone as Mobile,

        city as City,

        bill as Electricity_Bill,

        status as Status,

        note as Follow_Notes,

        follow_date as Follow_Date,

        created_at as Lead_Date

        FROM leads

        """,

        conn

    )



    file = "Har_Ghar_Solar_Leads.xlsx"


    df.to_excel(

        file,

        index=False

    )


    conn.close()





    # Excel Formatting

    wb = load_workbook(file)

    ws = wb.active



    ws.auto_filter.ref = ws.dimensions



    for column in ws.columns:


        max_length = 0


        col = column[0].column_letter



        for cell in column:


            if cell.value:


                max_length = max(

                    max_length,

                    len(str(cell.value))

                )


        ws.column_dimensions[col].width = max_length + 5



    wb.save(file)




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
# RUN SERVER
# ==========================


if __name__=="__main__":


    app.run(

    debug=True,

    port=5002

    )