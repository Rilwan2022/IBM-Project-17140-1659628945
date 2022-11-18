from flask import Flask, render_template, url_for, request, redirect, session, make_response
import sqlite3 as sql
from functools import wraps
import re
import ibm_db
import os
from markupsafe import escape
from flask_mail import Mail ,Message

from datetime import datetime, timedelta
from flask_login import LoginManager
login_manager = LoginManager()

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']="syedabdulr39@gmail.com"
app.config['MAIL_PASSWORD']="ipdsdogxbfneessb"
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)

app.secret_key = 'fasdgfdgdfg'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b70af05b-76e4-4bca-a1f5-23dbb4c6a74e.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32716;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xbz62710;PWD=tmYWG3ZF5n0bwLWE",'','')
print(conn)                                                                                                                                      
print("connection successful")

@app.route('/')
def home():
   return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST':
        ml = request.form['email']
        pd = request.form['password']
        sql = "SELECT * FROM users WHERE email =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, ml)
        ibm_db.bind_param(stmt, 2, pd)
        ibm_db.execute(stmt)
        record = ibm_db.fetch_assoc(stmt)
        print (record)
        if record:
            session['loggedin'] = True
            session[ml] = record
            return render_template('home.html',email=ml)
        else:
           return 'incorrect username'

 
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    mg = ''
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        pw = request.form['password']
        sql = 'SELECT * FROM users WHERE email =?'
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        acnt = ibm_db.fetch_assoc(stmt)
        print(acnt)

        if acnt:
            mg = 'Account already exits!!'

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mg = 'Please enter the avalid email address'
        elif not re.match(r'[A-Za-z0-9]+', username):
            ms = 'name must contain only character and number'
        else:
            insert_sql = 'INSERT INTO users (USERNAME,FIRSTNAME,LASTNAME,EMAIL,PASSWORD) VALUES (?,?,?,?,?)'
            pstmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(pstmt, 1, username)
            ibm_db.bind_param(pstmt, 2, firstname)
            ibm_db.bind_param(pstmt, 3, lastname)
            ibm_db.bind_param(pstmt, 4, email)
            ibm_db.bind_param(pstmt, 5, pw)
            print(pstmt)
            ibm_db.execute(pstmt)
            mg = 'You have successfully registered click login!'
           
           #sendgrid
            subject="new signup"
            message=Message(subject,sender="adnanshariqmd@gmail.com",recipients=[email]) 
            message.body="Registration successful"
            mail.send(message)
            return render_template("login.html", meg=mg)

    elif request.method == 'POST':
        msg = "fill out the form first!"
    return render_template("signup.html", meg=mg)







    # CODE TO ADD SSTOCKS


    

@app.route('/addstocks', methods=['POST','GET'])
# @login_required
def addStocks():
    if request.method == "POST":
      name = request.form['name']
      quantity = request.form['quantity']
      price = request.form['price']
      total = request.form['total']
      insert_sql = 'INSERT INTO stocks (NAME,QUANTITY,PRICE,TOTAL) VALUES (?,?,?,?)'
      pstmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(pstmt, 1, name)
      ibm_db.bind_param(pstmt, 2, quantity)
      ibm_db.bind_param(pstmt, 3, price)
      ibm_db.bind_param(pstmt, 4, total)
      ibm_db.execute(pstmt)
    # return render_template('list.html')
    # END OF CODE



#CODE FOR DASHBOARD



@app.route('/list/<email>')
def list(email):
  stocks = []
  sql = "SELECT * FROM stocks"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    ("The Name is : ",  dictionary)
    stocks.append(dictionary)
    print(stocks)
    dictionary = ibm_db.fetch_both(stmt)
  if stocks:
    return render_template("dashboard.html", stocks = stocks)
  else:
    subject="Empty stocks"
    message=Message(subject,sender="adnanshariqmd@gmail.com",recipients=[email]) 
    message.body="The inventory is empty"
    mail.send(message)
    msg="Currently the inventory is empty"
    return render_template("addstocks.html",msg=msg)  



@app.route('/delete/<name>')
def delete(name):
  sql = f"SELECT * FROM stocks WHERE name='{escape(name)}'"
  print(sql)
  stmt = ibm_db.exec_immediate(conn, sql)
  stocks = ibm_db.fetch_row(stmt)
  if stocks:
    sql = f"DELETE FROM stocks WHERE name='{escape(name)}'"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)

    stocks = []
    sql = "SELECT * FROM stocks"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      stocks.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    if stocks:
      return render_template("dashboard.html",  stocks= stocks, msg="Delete successfully")
#END 

@app.route("/addstockspage")
def addstocks():
    return render_template("addstocks.html")

@app.route("/signuppage")
def signuppage():
    return render_template("signup.html")    

