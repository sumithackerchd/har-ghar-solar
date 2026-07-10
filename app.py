from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask import send_file
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "harghar_solar_secret"

# DATABASE CREATE
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

        note TEXT DEFAULT ''

    )

    """)


    conn.commit()

    conn.close()



create_database()





@app.route("/")

def home():

    return render_template("index.html")





@app.route("/about")

def about():

    return render_template("about.html")





@app.route("/services")

def services():

    return render_template("services.html")





@app.route("/contact", methods=["GET","POST"])
def contact():

    if request.method=="POST":


        name=request.form["name"]

        phone=request.form["phone"]

        city=request.form["city"]

        bill=request.form["bill"]


        date=datetime.now().strftime("%d-%m-%Y %I:%M %p")


        conn=sqlite3.connect("solar.db")

        cur=conn.cursor()


        cur.execute(

        "INSERT INTO leads(name,phone,city,bill,created_at,status) VALUES(?,?,?,?,?,?)",

        (name,phone,city,bill,date,"New"))


        conn.commit()

        conn.close()


        return render_template(

        "thankyou.html",

        name=name,

        phone=phone,

        city=city,

        bill=bill

        )


    return render_template("contact.html")






@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method=="POST":

        username=request.form["username"]

        password=request.form["password"]


        if username=="admin" and password=="Solar@2026":

            session["admin"]=True

            return redirect("/admin")


    return render_template("login.html")



# Admin Dashboard

@app.route("/admin")
def admin():


    if "admin" not in session:

        return redirect("/admin-login")



    conn = sqlite3.connect("solar.db")

    cur = conn.cursor()



    cur.execute(

        "SELECT * FROM leads ORDER BY id DESC"

    )

    leads = cur.fetchall()




    cur.execute(

        "SELECT COUNT(*) FROM leads WHERE status='New'"

    )

    new_count = cur.fetchone()[0]




    cur.execute(

        "SELECT COUNT(*) FROM leads WHERE status='Contacted'"

    )

    contacted_count = cur.fetchone()[0]




    cur.execute(

        "SELECT COUNT(*) FROM leads WHERE status='Installed'"

    )

    installed_count = cur.fetchone()[0]




    conn.close()



    return render_template(

        "admin.html",

        leads=leads,

        new_count=new_count,

        contacted_count=contacted_count,

        installed_count=installed_count

    )

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

@app.route("/add-note/<int:id>", methods=["POST"])


def add_note(id):


    if "admin" not in session:

        return redirect("/admin-login")


    note=request.form["note"]


    conn=sqlite3.connect("solar.db")

    cur=conn.cursor()


    cur.execute(

    "UPDATE leads SET note=? WHERE id=?",

    (note,id)

    )


    conn.commit()

    conn.close()


    return redirect("/admin")

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

@app.route("/download-leads")


def download_leads():


    if "admin" not in session:

        return redirect("/admin-login")


    conn = sqlite3.connect("solar.db")

    cur = conn.cursor()


    cur.execute("SELECT * FROM leads")

    leads = cur.fetchall()


    conn.close()



    with open("solar_leads.csv","w",newline="") as file:


        writer = csv.writer(file)


        writer.writerow(

        [

        "ID",

        "Name",

        "Phone",

        "City",

        "Bill",

        "Date"

        ]

        )



        writer.writerows(leads)



    return send_file(

    "solar_leads.csv",

    as_attachment=True

    )

@app.route("/logout")

def logout():

    session.clear()

    return redirect("/")





if __name__=="__main__":

    app.run(debug=True, port=5002)