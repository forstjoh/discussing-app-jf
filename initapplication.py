from dbsettings import db
import usermanagement as users
from datetime import datetime, timezone

def dinitadmin(username, password, email):
    sql = "SELECT *, password FROM accounts WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return users.register(username, password, email, "admin")
    else:
        return True

