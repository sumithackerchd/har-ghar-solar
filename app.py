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
        created_at TEXT

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



        conn=sqlite3.connect("solar.db")

        cur=conn.cursor()


        date = datetime.now().strftime("%d-%m-%Y %I:%M %p")


        cur.execute(

        "INSERT INTO leads(name,phone,city,bill,created_at) VALUES(?,?,?,?,?)",

        (name,phone,city,bill,date))


        conn.commit()

        conn.close()



        return redirect("/")



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




@app.route("/admin")

def admin():


    if "admin" not in session:

        return redirect("/admin-login")


    conn=sqlite3.connect("solar.db")

    cur=conn.cursor()


    cur.execute("SELECT * FROM leads")


    data=cur.fetchall()


    conn.close()


    return render_template(
        "admin.html",
        leads=data
    )



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