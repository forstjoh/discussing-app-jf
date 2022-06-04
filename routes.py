from cgitb import text
import dbsettings
import dblib
from app import app
from flask import render_template, request, redirect, session, abort
import usermanagement as users
from sqlalchemy import true
from dbsettings import db
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

users.initadmin("admin", "a", "a.b@gmail.com")

@app.route("/usermgmt", methods=["GET", "POST"])
def usermgmt():
    if request.method == "GET":
        userlist = users.getusers()
        return render_template("usermgmt.html", users=userlist)
    if request.method == "POST":
        user = request.form["user"]
        details = users.getuserdetails(user)
        return render_template("usersdetails.html", details=details)

@app.route("/changeuser", methods=["POST"])
def changeuser():
    username = request.form["username"]
    if users.isadmin(session["username"]):
        remove = request.form.getlist('remove') 
        if len(remove) >0:
            if remove[0] == "yes":
                if users.removeuser(username) == True:
                    return redirect("/home?stoken="+session["csrf_token"])
                else:
                    return render_template("error.html", message="Cannot remove user "+username) 
        promo = request.form.getlist('promoteadmin')
        if len(promo) >0:
            app.logger.info(promo[0])
            if promo[0] == "yes":
                newrole = "admin"
            newrole = request.form["newrole"]
        newemail = request.form["newemail"]
        if newemail is None:
            newemail =""
        username = request.form["username"]
        users.changeuserdetails(username, newrole,newemail)
    return redirect("/home?stoken="+session["csrf_token"])

@app.route("/contentmgmt", methods=["GET", "POST"])
def contentmgmt():
    if request.method == "GET":
        areas = dblib.getdiscussionareas()
        userlist = users.getusers()
        return render_template("manageareas.html", discussionareas=areas, users=userlist)
    if request.method == "POST":
        selectedareas = request.form.getlist('areas')
        selectedpersons = request.form.getlist('users')
        users.giveacess(selectedareas, selectedpersons)
        return redirect("/home?stoken="+session["csrf_token"])

@app.route("/deleteright", methods=["GET", "POST"])
def deleteright():
    app.logger.info(session["username"])
    if request.method == "GET":
        return render_template("confirm.html")         
    if request.method == "POST":
        confirm = request.form["confirm"]
        if confirm == "yes":
            db.session.execute("DELETE FROM arearights")
            db.session.commit()
    return redirect("/home?stoken="+session["csrf_token"])

@app.route("/showright")
def showright():
    all = dblib.getallrights()
    return render_template("showright.html", rights=all)

@app.route("/removesomerights", methods=["POST"])
def removesomerights():
    rights = request.form.getlist('right')
    dblib.removerightlist(rights)
    return redirect("/home?stoken="+session["csrf_token"])

@app.route("/")
def index():
    if not session.get('csrf_token'):
        session["csrf_token"] = secrets.token_hex(16)
    if not session.get('loggedin'):
        session["loggedin"] = "False" 
        return redirect("/login")
    elif session.get('loggedin') == "True":
        url = "/home?stoken="+session["csrf_token"]
        return redirect(url)
    elif session.get('loggedin') == "False":
        return redirect("/login")
    else:
        return render_template("error.html", message="Internal error")

@app.route("/home")
def home():
    if not session.get('loggedin'):
        session["loggedin"] = "False" 
    if session["loggedin"] == "True":
        sessiontoken = request.args.get('stoken')
        if sessiontoken == None:
            return redirect("/logout")
        if session["csrf_token"] != sessiontoken:
            return redirect("/logout")
    if 'showareas' in session:
        if session["showareas"] == "True":
            if session.get("username"):
                username=session["username"]
            else:
                app.logger.info("user EI ok ")
                users.logout()
                return render_template("index.html")
            areas = dblib.getareasforuser(username)
            return render_template("index.html", discussionareas=areas) 
        else:
            return render_template("index.html") 
    else:
        return render_template("index.html") 

@app.route("/addnewarea", methods=["GET", "POST"])
def addnewarea():
    if request.method == "GET":
        return render_template("newarea.html")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
           abort(403)
        area = request.form["full_name"]
        creator = session["username"]
        if dblib.addnewareax(area, creator) == False:
            return render_template("error.html", message="Cannot add area, name must be unique")
        return redirect("/home?stoken="+session["csrf_token"])

@app.route("/addnewchain/<int:area_id>", methods=["GET", "POST"])
def addnewchain(area_id):
    a = int(area_id)
    area = dblib.getareadetails(a)
    if request.method == "GET":
        return render_template("newchain.html", area=area )
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
           abort(403)
        areaid = request.form["area"]
        creator = session["username"]
        full_name = request.form["fullname"]
        description = request.form["description"]
        dblib.addnewchain(area, full_name, description, creator)
        return redirect("/home?stoken="+session["csrf_token"])

@app.route("/addnewmessage/<int:chain_id>", methods=["GET", "POST"])
def addnewmessage(chain_id):
    c = int(chain_id)
    chain = dblib.getchaindetails(c)
    if request.method == "GET":
        return render_template("newmessage.html", chain=chain )
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
           abort(403)
        area = request.form["area"]
        creator = session["username"]
        subject = request.form["subject"]
        text = request.form["messagetext"]
        dblib.addnewmessage(area, c, subject, text, creator)
        return redirect("/home?stoken="+session["csrf_token"])

@app.route("/enterareax", methods=["POST"])
def enterareax():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    areaid = request.form["area"]
    a = int(areaid)
    area = dblib.getareadetails(a)
    chains = dblib.getchains(a)
    return render_template("chain.html", area=area, chains = chains )

@app.route("/enterchainx", methods=["POST"])
def enterchainx():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    chainid = request.form["chain"]
    areaid = request.form["area"]
    c = int(chainid)
    a = int(areaid)
    area = dblib.getareadetails(a)
    chain = dblib.getchaindetails(c)
    messages = dblib.getmessages(a,c)
    return render_template("messages.html", area=area, chain=chain, messages = messages )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/home?stoken="+session["csrf_token"])
        else:
            return render_template("error.html", message="Wrong user id or password")


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        email = request.form["email"]
        role  = request.form["role"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        email = request.form["email"]
        role  = request.form["role"]
        
        if users.register(username, password1, email, role):
            return redirect("/home?stoken="+session["csrf_token"])
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        username = session["username"]
        searchstring = request.form["searchstring"]
        areas = dblib.searchareas(username, searchstring)
        allareas = dblib.getareasforuser(username)
        chains = None
        messages = None
        if len(areas) == 0:
            areas = None
        chains = dblib.searchchains(username, searchstring, allareas)
        if len(chains) == 0:
            chains = None
        messages = dblib.searchmessages(username, searchstring, allareas, chains)
        if len(messages) == 0:
            messages = None
        return render_template("searchresults.html", searchstring=searchstring,  areas=areas, chains=chains, messages = messages )

