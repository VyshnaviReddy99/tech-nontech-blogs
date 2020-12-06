from flask import Flask,request,render_template,redirect,flash,jsonify
import re
import bcrypt
import json
import math, random
import smtplib
from flask_restful import Resource,Api,reqparse
import json
import jwt
from datetime import datetime as dt
from datetime import timedelta
import sqlite3
#from flask_login import login_required, current_user

connection=sqlite3.connect('mydb.db')
cursor=connection.cursor()
#cursor.execute("DROP TABLE Users")
#create_table='''CREATE TABLE Users(
#   username TEXT NOT NULL,
#   email TEXT NOT NULL PRIMARY KEY,
#   password TEXT NOT NULL)'''
#cursor.execute(create_table)
#cursor.execute("DROP TABLE POSTS")
#create_table2='''CREATE TABLE POSTS(
#      email TEXT NOT NULL,
#      title TEXT NOT NULL,
#      imagepath TEXT NOT NULL,
#      description TEXT NOT NULL)'''
#cursor.execute(create_table2)
connection.commit()
cursor.close()


app=Flask(__name__)
app.config['SECRET_KEY']='qwertyuiop'
session={}

@app.route("/")
def indexform():
    return render_template('index.html')

@app.route("/login")
def form():
   if(session=={}):
      return render_template('login.html')

def fetchusers():
   conn=sqlite3.connect('mydb.db')
   c2=conn.cursor()
   c2.execute("SELECT title,imagepath,description from POSTS")
   f=c2.fetchall()
   conn.commit()
   c2.close()
   #print(list(f))
   return list(f)

@app.route("/home",methods=['POST'])
def success():
   e2=request.form['email']
   p2=request.form['password']
   p3=p2.encode('utf-8')
   #with open('users_details.json','r') as f:
      #data=json.load(f)
   conn=sqlite3.connect('mydb.db')
   c1=conn.cursor()
   c1.execute("SELECT email,password,username FROM Users WHERE email= ?",(e2,))
   f=c1.fetchone()
   conn.commit()
   c1.close()
   if(f):
      if f[0]==e2 :
         t=f[1]
         u=t.encode('utf-8')
         if bcrypt.checkpw(p3,u):
            fetched = fetchusers()
            session['email']=e2
            print(session['email'])
            session['username']=f[2]
            sessionusername=session['username']
            return render_template("home.html",length = len(fetched), fetched=fetched, name=sessionusername)
         else:
            #return flash("Failed to sign in")
            return "Failed to sign in"
   else:
      return "User does not exists"
@app.route("/backtohome")
def backtohome():
   fetched = fetchusers()
   sessionusername=session['username']
   return render_template("home.html",length = len(fetched), fetched=fetched, name=sessionusername)

@app.route("/createblog")
def createblog():
    return render_template('createblog.html')

@app.route("/postcreateblog",methods=["POST"])
def postcreateblog():
   #print(request.form.to_dict())
   email=session['email']
   title=request.form['title']
   content=request.form['content']

   conn1=sqlite3.connect('mydb.db')
   c6=conn1.cursor()
   c6.execute("INSERT INTO POSTS (email,title,imagepath, description) VALUES (?, ?,?, ?)", (email,title,"bcudcbbc",content))
   conn1.commit()
   c6.close()
   return "Posted"

@app.route("/myblogs")
def myblogs():
   conn=sqlite3.connect('mydb.db')
   c4=conn.cursor()
   sessionemail=session['email']
   c4.execute("SELECT title,imagepath,description from POSTS where email=(?)",(sessionemail,))
   f1=c4.fetchall()
   f1=list(f1)
   conn.commit()
   c4.close()
   if len(f1)==0:
      return "You dont have any blogs"
   else:
      return render_template('myblogs.html',length = len(f1), fetched=f1)

@app.route("/ondeleteblog/<title>")
def ondeleteblog(title):
   conn=sqlite3.connect('mydb.db')
   c5=conn.cursor()
   sessionemail=session['email']
   print(title)
   c5.execute("DELETE from POSTS where email=(?) and title=(?)",(sessionemail,title))
   c5.execute("SELECT title,imagepath,description from POSTS where email=(?)",(sessionemail,))
   f1=c5.fetchall()
   f1=list(f1)
   conn.commit()
   c5.close()
   if len(f1)==0:
      return "You dont have any blogs"
   else:
      return render_template('myblogs.html',length = len(f1), fetched=f1)

digits = "0123456789"
OTP = ""
for _ in range(4) : 
   OTP += digits[math.floor(random.random() * 10)]
o1=OTP.encode('utf-8')
hasho1=bcrypt.hashpw(o1,bcrypt.gensalt())


@app.route("/forgotpass",methods=['POST'])
def forgotpass():
   s = smtplib.SMTP('smtp.gmail.com', 587)
   s.starttls()
   f=open('password.txt').read()
   s.login("vyshnavigeetla@gmail.com", f)
   msg='Your OTP for Verification is '+OTP
   s.sendmail('vyshnavigeetla@gmail.com',request.form['email'],msg)
   return render_template('forgotpass.html')

@app.route("/forgotpassvalidate",methods=['POST'])
def passvalidate():
   o2=request.form['otp']
   if o2==OTP:
      return render_template('resetpass.html')
   else:
      return render_template('postvalidunsuccess.html')

@app.route("/resetsuccess",methods=['POST'])
def resetsuccess():
      p1=request.form['password']
      p=p1.encode('utf-8')
      hashp1=bcrypt.hashpw(p,bcrypt.gensalt())
      with open('users_details.json', 'r') as f:
         test_dict = json.load(f)
      test_dict.update({'Password':hashp1.decode()})
      y=json.dumps(test_dict)
      with open('users_details.json','wb') as f:
         f.write(y.encode())
         return render_template('postreset.html')

@app.route("/signup", methods=['GET','POST'])
def signup():
   return render_template('signup.html')

@app.route("/OtpConfirmation",methods=['POST'])
def otp():
   u1=request.form['username']
   e1=request.form['email']
   p1=request.form['password']
   p=p1.encode('utf-8')
   hashp1=bcrypt.hashpw(p,bcrypt.gensalt())
   user={'Username':u1,'Email':e1,'Password':hashp1.decode(),'OTPGenerated':hasho1.decode()}
   x=json.dumps(user)
   with open('users_details.json','wb') as f:
      f.write(x.encode())
   s = smtplib.SMTP('smtp.gmail.com', 587)
   s.starttls()
   f=open('password.txt').read()
   s.login("vyshnavigeetla@gmail.com", f)
   msg='Your OTP for Verification is '+OTP
   s.sendmail('vyshnavigeetla@gmail.com',request.form['email'],msg)
   return render_template('otp_page.html')

@app.route("/validate",methods=['POST'])
def validate():
   o2=request.form['otp']
   o3=o2.encode('utf-8')
   if bcrypt.checkpw(o3,hasho1):
      with open('users_details.json', 'r') as f:
         test_dict = json.load(f)
      new_dict = {key:val for key, val in test_dict.items() if key != 'OTPGenerated'}
      x=json.dumps(new_dict)
      with open('users_details.json','w') as f:
         f.write(x)
      userdb=new_dict["Username"]
      emaildb=new_dict["Email"]
      passdb=new_dict["Password"]
      conn=sqlite3.connect('mydb.db')
      c=conn.cursor()
      #insert_details = "INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (userdb,emaildb,passdb)
      c.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (userdb,emaildb,passdb))
      conn.commit()
      c.close()

      return render_template('postvalidation.html')
   else:
      return render_template('postvalidunsuccess.html')

@app.route("/logout")
def onlogout():
   session.pop('email',None)
   session.pop('username',None)
   return render_template('index.html')


if __name__=="__main__":
    app.run(debug =True)