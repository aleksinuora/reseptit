from db import db
from werkzeug.security import check_password_hash, generate_password_hash

def find_user(username):
    sql = "SELECT id, passhash \
        FROM userprofile WHERE userprofile_name=:username"
    return db.session.execute(sql, {"username":username}).fetchone()

def get_username(id):
    sql = "SELECT userprofile_name \
        FROM userprofile WHERE id=:id"
    return db.session.execute(sql, {"id":id}).fetchone()["userprofile_name"]

def add_user(username, password):
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO userprofile (userprofile_name, passhash) \
        VALUES (:username, :hash_value)"
    db.session.execute(sql, {"username":username, "hash_value":hash_value})
    db.session.commit()
    