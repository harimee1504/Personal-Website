from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
import smtplib
import urllib
from sqlalchemy import text
from email.message import EmailMessage
from datetime import datetime, date
from dateutil.relativedelta import *


app = Flask(__name__)

app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="Your Username",
    password="Your Password",
    hostname="Your Password",
    databasename="Your database name",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


def sendmail(receiver, url, tit, name, r):
    Email_PASSWORD = "Your password"
    Email_ADDRESS = "Your email address"
    msg = EmailMessage()
    msg['From'] = Email_ADDRESS
    msg['To'] = receiver
    if r == 0:
        msg['Subject'] = 'Price Fell Down'
        mg = "Dear "+name+":\n\n"+"Your Product Price Fell Down below your Desired Price:\n\n" + \
            "Check it out:\n\n"+tit+"\n\n"+url
    else:
        msg['Subject'] = 'Amazon Price Traker'
        mg = "Dear "+name+":\n\n"+"Your Product Price is still above your Desired Price.\n\n" + \
            "We Will Notify you when Price fell down."+"\n\n"+tit+"\n\n"+url
    msg.set_content(mg)

    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login(Email_ADDRESS, Email_PASSWORD)
    smtp.send_message(msg)
    smtp.quit()


def execute(query):
    t = text(query)
    result = db.session.execute(t)
    res = result.fetchall()
    return res


cities = []
groups = ['A +ve', 'A -ve', 'B +ve', 'B -ve',
          'AB +ve', 'AB -ve', 'O +ve', 'O -ve']


def status(group):
    fn = "SELECT fname FROM "+group
    ln = "SELECT lname FROM "+group
    t = "SELECT active FROM "+group
    s = "SELECT NextDonate FROM "+group
    ci = "SELECT city FROM "+group
    t = execute(t)
    fn = execute(fn)
    ln = execute(ln)
    s = execute(s)
    ci = execute(ci)
    t1, s1, fn1, ln1 = [], [], [], []
    for i in range(len(t)):
        for j in t[i].values():
            t1.append(j)
        for k in s[i].values():
            s1.append(k)
        for l in fn[i].values():
            fn1.append(l)
        for n in ln[i].values():
            ln1.append(n)
        for m in ci[i].values():
            if m not in cities:
                cities.append(m)
    tot = len(t)
    act = 0
    for i in range(len(t)):
        if t1[i] == 'active':
            act += 1
        else:
            today = list(map(int, str(date.today()).split('-')))
            y = list(map(int, str(s1[i]).split('-')))
            d1 = datetime(y[0], y[1], y[2])
            d2 = datetime(today[0], today[1], today[2])
            x = text("update "+group+" set active=:act WHERE fname=:fname AND lname=:lname")\
                .bindparams(act="active", fname=fn1[i], lname=ln1[i])
            if d2 > d1:
                db.session.execute
                db.session.commit()
    res = [tot, act]
    return res


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "GET":
        return redirect('/')
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        Email_PASSWORD = "JO8NC5NAaa"
        Email_ADDRESS = "hariwebpage@gmail.com"

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Email_ADDRESS
        msg['To'] = Email_ADDRESS
        mg = "Name: "+name+"\n\n"+"E-Mail: "+email+"\n\n" + \
            "Subject: "+subject+"\n\n"+"Message: "+message
        msg.set_content(mg)

        msg1 = EmailMessage()
        msg1['Subject'] = "Thank you For your Comment"
        msg1['From'] = Email_ADDRESS
        msg1['To'] = email
        mg1 = "Thank you "+name+" for your precious comment.\n" + \
            "Always happy to hear from you.\n"+"For Further Contact:\n"+"Phone: +91-9080053714"
        msg1.set_content(mg1)
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(Email_ADDRESS, Email_PASSWORD)
        smtp.send_message(msg)
        smtp.send_message(msg1)
        smtp.quit()
        return redirect('/')


@app.route('/blood-index')
def bloodindex():
    blood = ['apositive', 'anegative', 'bpositive', 'bnegative',
             'abpositive', 'abnegative', 'opositive', 'onegative']
    total, active, inactive = [], [], []
    for i in blood:
        res = status(i)
        if len(res) != 0:
            total.append(str(res[0]))
            active.append(str(res[1]))
            inactive.append(str(res[0]-res[1]))
    td = sum([int(i) for i in total])
    ad = sum([int(i) for i in active])
    id1 = sum([int(i) for i in inactive])
    cities.sort()
    return render_template("bloodindex.html", total=total, active=active, inactive=inactive, td=td, ad=ad, id1=id1, cities=cities, groups=groups)


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        group = request.form.get("group")
        area = request.form.get("area")
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")
        dob = request.form.get("dob")
        phone = request.form.get("phone")
        email = request.form.get("email")
        firstDonate = request.form.get("first")
        if firstDonate == 'no':
            LastDonate = request.form.get("LastDonate")
            ld = datetime.strptime(LastDonate, '%Y-%m-%d').date()
            NextDonate = ld+relativedelta(months=+4)
            today = list(map(int, str(date.today()).split('-')))
            NextDonate = list(map(int, str(NextDonate).split('-')))
            d1 = datetime(NextDonate[0], NextDonate[1], NextDonate[2])
            d2 = datetime(today[0], today[1], today[2])
            ldtemp = str(NextDonate[0])+'-' + \
                str(NextDonate[1])+'-'+str(NextDonate[2])
            if d2 > d1:
                stat = 'active'
            else:
                stat = 'inactive'
        else:
            stat = 'active'
            LastDonate = 'Donor-Time-First'
            ldtemp = 'First'

        table = text("INSERT INTO "+group+" (fname,lname,area,city,state,country,dob,phone,email,LastDonate,active,NextDonate) VALUES(:fname,:lname,:area,:city,:state,:country,:dob,:phone,:email,:LastDonate,:active,:NextDonate)")\
            .bindparams(fname=fname, lname=lname, area=area, city=city, state=state, country=country, dob=dob, phone=phone, email=email, LastDonate=LastDonate, active=stat, NextDonate=ldtemp)
        db.session.execute(table)
        db.session.commit()
        return redirect('/blood-index')


@app.route('/apositive')
def apositive():
    t = execute('SELECT * FROM apositive')
    return render_template('details.html', t=t, n=len(t), group='A positive ')


@app.route('/bpositive')
def bpositive():
    t = execute('SELECT * FROM bpositive')
    return render_template('details.html', t=t, n=len(t), group='B positive ')


@app.route('/abpositive')
def abpositive():
    t = execute('SELECT * FROM abpositive')
    return render_template('details.html', t=t, n=len(t), group='AB positive ')


@app.route('/opositive')
def opositive():
    t = execute('SELECT * FROM opositive')
    return render_template('details.html', t=t, n=len(t), group='O positive ')


@app.route('/anegative')
def anegative():
    t = execute('SELECT * FROM anegative')
    return render_template('details.html', t=t, n=len(t), group='A negative ')


@app.route('/bnegative')
def bnegative():
    t = execute('SELECT * FROM bnegative')
    return render_template('details.html', t=t, n=len(t), group='B negative ')


@app.route('/abnegative')
def abnegative():
    t = execute('SELECT * FROM abnegative')
    return render_template('details.html', t=t, n=len(t), group='AB negative ')


@app.route('/onegative')
def onegative():
    t = execute('SELECT * FROM onegative')
    return render_template('details.html', t=t, n=len(t), group='O negative ')


@app.route('/search', methods=["GET", "POST"])
def find():
    grp = ['apositive', 'anegative', 'bpositive', 'bnegative',
           'abpositive', 'abnegative', 'opositive', 'onegative']
    if request.method == "GET":
        return redirect('/blood-index')
    else:
        s1 = request.form.get("city")
        s2 = request.form.get("groups")
        if s2 == 'Select Group' or s1 == 'Select City':
            return redirect('/blood-index')
        else:
            ind = groups.index(s2)
            val = 'SELECT * FROM '+grp[ind]+' WHERE city="'+s1+'";'
        t = execute(val)
        c1, c2 = 0, 0
        for i in range(len(t)):
            if t[i]['active'] == 'active':
                c1 += 1
            else:
                c2 += 1
        grp[ind] = grp[ind].lower().capitalize()
        grp[ind] = grp[ind][:1]+' '+grp[ind][1:]
        return render_template('details.html', t=t, n=len(t), group=grp[ind], c1=c1, c2=c2)


@app.route("/pro")
def view():
    t = execute("SELECT * FROM Project")
    return render_template("view.html", t=t, n=len(t))


@app.route('/log', methods=['GET', 'POST'])
def log():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin1234@gmail.com' or request.form['password'] != 'admin1234':
            error = 'Invalid Credentials.'
        else:
            return redirect("/proindex")
    return render_template('log.html', error=error)


@app.route('/proindex')
def proindex():
    t = execute("SELECT * FROM Project")
    return render_template("pro-index.html", t=t, n=len(t))


@app.route('/proadd', methods=["GET", "POST"])
def add1():
    if request.method == "GET":
        return render_template("pro-add.html")
    else:
        name = request.form.get("name")
        des = request.form.get("des")
        url = request.form.get("url")
        phn = request.form.get("phn")
        cphn = request.form.get("cphn")
        x = text("INSERT INTO Project (name,des,url,phn,cphn) VALUES(:name,:des,:url,:phn,:cphn)")\
            .bindparams(name=name, des=des, url=url, phn=phn, cphn=cphn)
        db.session.execute(x)
        db.session.commit()
        if phn != cphn:
            return render_template("wrong.html", name=urllib.parse.unquote(name), des=urllib.parse.unquote(des), url=url, phn=phn, cphn=cphn)
        else:
            return redirect("/pro")


@app.route('/delete/<name>/<des>', methods=["GET", "POST"])
def delete(name, des):
    x = text("DELETE FROM Project WHERE name=:name AND des=:des")\
        .bindparams(name=name, des=des)
    db.session.execute(x)
    db.session.commit()
    return redirect("/proindex")


@app.route('/delall')
def delall():
    db.session.execute("DELETE FROM Project")
    db.session.commit()
    return redirect("/pro")


@app.route('/edit/<name>/<des>/<path:url>/<phn>/<cphn>', methods=["GET", "POST"])
def edit(name, des, url, phn, cphn):
    if request.method == "GET":
        return render_template("edit.html", name=urllib.parse.unquote(name), des=urllib.parse.unquote(des), url=url, phn=phn, cphn=cphn)
    else:
        uname = request.form.get("name-edit")
        udes = request.form.get("des-edit")
        uurl = request.form.get("url-edit")
        uphn = request.form.get("phn-edit")
        ucphn = request.form.get("cphn-edit")
        x = text("update Project set name=:uname , des=:udes , url=:uurl , phn=:uphn , cphn=:ucphn WHERE name=:name AND des=:des")\
            .bindparams(uname=uname, udes=udes, uurl=uurl, uphn=uphn, ucphn=ucphn, name=name, des=des)
        db.session.execute(x)
        db.session.commit()
        return redirect("/pro")


@app.route('/wrong/<name>/<des>/<path:url>/<phn>/<cphn>', methods=["GET", "POST"])
def wrong(name, des, url, phn, cphn):
    if request.method == "GET":
        return render_template("edit.html", name=urllib.parse.unquote(name), des=urllib.parse.unquote(des), url=url, phn=phn, cphn=cphn)
    else:
        uname = request.form.get("name")
        udes = request.form.get("des")
        uurl = request.form.get("url")
        uphn = request.form.get("phn")
        ucphn = request.form.get("cphn")
        x = text("update Project set name=:uname , des=:udes , url=:uurl , phn=:uphn , cphn=:ucphn WHERE name=:name AND des=:des")\
            .bindparams(uname=uname, udes=udes, uurl=uurl, uphn=uphn, ucphn=ucphn, name=name, des=des)
        db.session.execute(x)
        db.session.commit()
        return redirect("/pro")
