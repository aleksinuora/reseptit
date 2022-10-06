from db import db
import datetime

def get_recipe_comments(id):
    sql = "\
        WITH c AS (\
            SELECT * \
            FROM comment \
            WHERE recipe_id = :id \
        ), \
        u AS (\
            SELECT \
                userprofile.id AS userprofile_id, \
                userprofile.userprofile_name \
            FROM userprofile, c \
            WHERE userprofile.id = c.userprofile_id\
        ) \
        SELECT DISTINCT \
            c.id, c.content, c.sent_at, c.userprofile_id, \
            c.recipe_id, u.userprofile_name \
        FROM c \
        JOIN \
        u \
        ON c.userprofile_id = u.userprofile_id \
        ORDER BY c.sent_at DESC \
        "
    return db.session.execute(sql, {"id":id}).fetchall()

def get_user_comments(username):
    sql = "WITH uid AS (\
            SELECT id \
            FROM userprofile \
            WHERE userprofile_name=:username \
        )\
        SELECT * \
        FROM comment, uid \
        WHERE userprofile_id=uid.id"
    result = db.session.execute(sql, {"username":username})
    return result.fetchall()

def send_recipe_comment(content, user_id, recipe_id):
    current_timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    sql = "\
        INSERT INTO comment \
            (content, sent_at, userprofile_id, recipe_id) \
        VALUES \
            (:content, :current_timestamp, :user_id, :recipe_id)"    
    result = db.session.execute(sql, {"content":content, \
        "current_timestamp":current_timestamp, "user_id":user_id, \
        "recipe_id":recipe_id}) 
    db.session.commit()

def delete_comment(id):
    sql = "DELETE FROM comment WHERE id = :id"
    db.session.execute(sql, {"id":id})
    db.session.commit()