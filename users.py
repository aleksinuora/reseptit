from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session

def find_user(username):
    sql = "SELECT id, userprofile_name, passhash \
        FROM userprofile WHERE userprofile_name=:username"
    return db.session.execute(sql, {"username":username}).fetchone()

def get_username(id):
    sql = "SELECT userprofile_name \
        FROM userprofile WHERE id=:id"
    return db.session.execute(sql, {"id":id}).fetchone()["userprofile_name"]

def add_user(username, password):
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO userprofile (userprofile_name, passhash) \
        VALUES (:username, :hash_value) \
        ON CONFLICT(userprofile_name) DO NOTHING \
        RETURNING userprofile_name"
    result = db.session.execute(sql, {"username":username, "hash_value":hash_value}).fetchone()
    db.session.commit()
    return result

def delete_userprofile(username, session_user):
    sql = "DELETE FROM userprofile WHERE userprofile_name=:username"
    db.session.execute(sql, {"username":username})

    if session_user != "Testaaja":
        db.session.commit()

def get_users():
    sql = "SELECT id, userprofile_name FROM userprofile ORDER BY userprofile_name ASC"
    result = db.session.execute(sql)
    return result.fetchall()