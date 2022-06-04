
from sqlalchemy import true
from dbsettings import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
from app import app
import secrets


def initadmin(username, password, email):
    sql = "SELECT *, password FROM accounts WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return register(username, password, email, "admin")
    else:
        return True

def getusers():
    sql = "SELECT * FROM accounts"
    result = db.session.execute(sql)
    users = result.fetchall()
    return users

def giveacess(areas, users):
    for area_id in areas:
        for username in users:
            app.logger.info("user "+username)  
     
            sqluser = "SELECT user_id FROM accounts WHERE username=:username "
            result = db.session.execute(sqluser, {"username":username})
            user_id = result.fetchone()[0]

            sqltest = "SELECT * FROM arearights WHERE area_id=:area_id AND user_id=:user_id"
            result = db.session.execute(sqltest, {"area_id":area_id, "user_id":user_id})
            
            testres = result.fetchall()

            if not testres:
                sqlarea = "INSERT INTO arearights (area_id,user_id) VALUES (:area_id,:user_id)"  
                db.session.execute(sqlarea, {"area_id":area_id, "user_id":user_id})
                db.session.commit()

def register(username, password, email, role):
    hash_value = generate_password_hash(password)
    created_on = datetime.now()
    try:
        sql = "INSERT INTO accounts (username,password,email,role,created_on) VALUES (:username,:password,:email,:role,:created_on)"
        db.session.execute(sql, {"username":username, "password":hash_value, "email":email, "role":role, "created_on":created_on})
        db.session.commit()
        return True
    except:
        return False

def removeuser(username):
    try:    
        if isadmin(session["username"]):
            sql = "DELETE FROM accounts WHERE username = :username"
            result = db.session.execute(sql, {"username":username})
            db.session.commit()
            return True
    except:
        return False

def changerole(username, newrole):
    try:    
        if isadmin(session["user_id"]):
            sql = "UPDATE accounts SET role=:newrole WHERE username = :username"
            result = db.session.execute(sql, {"role":newrole, "username":username})
            return True
    except:
        return False

def changeuserdetails(username, role, email, password):
    if len(email) == 0:
        sql = "UPDATE accounts SET role=:role WHERE username = :username"
        result = db.session.execute(sql, { "role":role, "username":username })
    else:
        sql = "UPDATE accounts SET email=:email, role=:role WHERE username = :username"
        result = db.session.execute(sql, {"email":email, "role":role, "username":username })
    db.session.commit()

    if len(password) > 0:
        changepassword(username, password)
    
    
def changepassword(username, newpassword):
    password = generate_password_hash(newpassword)
    sql = "UPDATE accounts SET password=:password WHERE username = :username"
    result = db.session.execute(sql, {"username":username, "password":password})
    db.session.commit()  


    
    

def isadmin(username):
    sql ="SELECT role FROM accounts WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    role = result.fetchone()   
    print(role[0])
    if role[0] == "admin":
        return True
    else: 
        return False

def getuserdetails(username):
    sql = "SELECT * FROM accounts WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    return user

def login(username, password):
    sql = "SELECT *, password FROM accounts WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["username"] = user.username
            session["role"] = user.role
            session["showareas"] = "True"
            session["loggedin"] = "True"
            last_login = datetime.now()
            username = user.username
            sql = "UPDATE accounts SET last_login=:last_login WHERE username = :username"
            result = db.session.execute(sql, {"username":username, "last_login":last_login})
            db.session.commit()        
            return True
        else:
            return False

def logout():
    session.clear()
    session["showareas"] = "False"

def user_id():
    return session.get("user_id",0)