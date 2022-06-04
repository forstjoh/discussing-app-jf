from sqlalchemy import true
from dbsettings import db
from app import app
from datetime import datetime, timezone


def getdiscussionareas():
    sql = "SELECT * FROM discussion_areas"
    result = db.session.execute(sql)
    areas = result.fetchall()
    return areas

def getchains(areaid):
    area_id = int(areaid)
    sql = "SELECT * FROM chains WHERE area_id=:area_id"
    result = db.session.execute(sql, {"area_id":area_id})
    chainlist = result.fetchall()
    return chainlist

def getareadetails(areaid):
    area_id = int(areaid)
    sql = "SELECT * FROM discussion_areas WHERE area_id=:area_id"
    result = db.session.execute(sql, {"area_id":area_id})
    area   = result.fetchone()
    return area 

def getchaindetails(chain):
    chain_id = int(chain)
    sql = "SELECT * FROM chains WHERE chain_id=:chain_id"
    result = db.session.execute(sql, {"chain_id":chain_id})
    ch   = result.fetchone()
    return ch 

def getmessages(area, chain):
    area_id = int(area)
    chain_id = int(chain)
    sql = "SELECT * FROM message WHERE area_id=:area_id AND chain_id=:chain_id"
    result = db.session.execute(sql, {"area_id":area_id, "chain_id":chain_id})
    msglist = result.fetchall()
    return msglist

def removerightlist(rights):
    for id in rights:
        sql = "DELETE FROM arearights WHERE id = :id"
        result = db.session.execute(sql, {"id":id})
        db.session.commit()

def addnewchain(area, full_name, description, creator):
    try:
        created_at = datetime.now()
        area_id = int(area["area_id"])
        sql = "INSERT INTO chains (area_id, full_name,description,creator,created_at) VALUES (:area_id,:full_name,:description,:creator,:created_at)"
        db.session.execute(sql, {"area_id":area_id, "full_name":full_name,"description":description, "creator":creator, "created_at":created_at})
        db.session.commit()
        return True
    except:
        return False

def addnewmessage(area, chain, full_name, message_text, creator):
    try:
        area_id = int(area)
        chain_id = int(chain)
        created_at = datetime.now()
        sql = "INSERT INTO message (area_id, chain_id, full_name, message_text,creator,created_at) VALUES (:area_id,:chain_id,:full_name,:message_text,:creator,:created_at)"
        db.session.execute(sql, {"area_id":area_id, "chain_id":chain_id,  "full_name":full_name,"message_text":message_text, "creator":creator, "created_at":created_at})
        db.session.commit()
        return True
    except:
        return False

def addnewareax(full_name, creator):
    try:
        created_at = datetime.now()
        sql = "INSERT INTO discussion_areas (full_name,creator,created_at) VALUES (:full_name,:creator,:created_at)"
        result = db.session.execute(sql, {"full_name":full_name, "creator":creator, "created_at":created_at})
        db.session.commit()
        addsingleright(full_name, creator)
        return True
    except:
        return False

def getallrights():
    sql = "SELECT * FROM arearights GROUP BY id, user_id ORDER BY area_id"
    result = db.session.execute(sql)
    rightlist = result.fetchall()
    return rightlist

def getareasforuser(username):
    sql = "SELECT user_id FROM accounts WHERE username = :username"
    result = db.session.execute(sql, {"username": username})
    user_id = result.fetchone()[0]
    sql = "SELECT D.* FROM discussion_areas D, arearights A WHERE D.area_id = A.area_id AND A.user_id = :user_id"
    result = db.session.execute(sql, {"user_id": user_id})
    rightlist = result.fetchall()
    return rightlist
    
def addsingleright(full_name, username):
    try:
        sqluser = "SELECT user_id FROM accounts WHERE username=:username"
        result = db.session.execute(sqluser, {"username":username})
        user_id = result.fetchone()[0]
        sqluser = "SELECT area_id FROM discussion_areas WHERE full_name=:full_name"
        result = db.session.execute(sqluser, {"full_name":full_name})
        area_id = result.fetchone()[0]
        sqlarea = "INSERT INTO arearights (area_id,user_id) VALUES (:area_id,:user_id)"  
        db.session.execute(sqlarea, {"area_id":area_id, "user_id":user_id})
        db.session.commit()
        return True
    except:
        return False

def getuseridbyname(username):
    sql = "SELECT user_id FROM accounts WHERE username = :username"
    result = db.session.execute(sql, {"username": username})
    user_id = result.fetchone()[0]
    return user_id

def searchareas(username, searchstring):
    user_id = getuseridbyname(username)
    sql = "SELECT D.* FROM discussion_areas D, arearights A WHERE D.area_id = A.area_id AND A.user_id = :user_id AND D.full_name LIKE :searchstring"
    result = db.session.execute(sql, {"user_id": user_id, "searchstring":"%"+searchstring+"%"} )
    rightlist = result.fetchall()
    return rightlist

def searchchains(username, searchstring, areas):
    user_id = getuseridbyname(username)
    if len(areas) > 0:
        for area in areas:
            areaid = area[0]
            sql = "SELECT C.* FROM chains C, discussion_areas D WHERE D.area_id = C.area_id AND (C.full_name LIKE :searchstring OR C.description LIKE :searchstring)"
            result = db.session.execute(sql, {"user_id": user_id, "searchstring":"%"+searchstring+"%"} )
            rightlist = result.fetchall()
        return rightlist 
    else:
        return []

def searchmessages(username, searchstring, areas, chains):
    returnlist =[]
    for area in areas:
        area_id = area[0]
        sql = "SELECT M.* FROM message M WHERE M.area_id = :area_id AND (M.full_name LIKE :searchstring OR M.message_text LIKE :searchstring)"
        result = db.session.execute(sql, {"area_id": area_id,"searchstring":"%"+searchstring+"%"} )
        rightlist = result.fetchall()
        if len(rightlist) >0:
            returnlist.extend(rightlist)
    return returnlist
