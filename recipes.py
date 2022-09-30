from db import db
import datetime

def get_recipe(id):
    sql = "SELECT \
            R.recipe_name, R.passive_time, R.active_time, \
            R.recipe_description, R.created_at, \
            J.quantity, J.unit, I.ingredient_name \
        FROM \
            recipe R, ingredient I, recipeingredient J\
        WHERE \
            R.id=:id \
            AND J.recipe_id=:id \
            AND I.id=J.ingredient_id"
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def get_random_recipe():
    sql = "SELECT \
            id, recipe_name, passive_time, active_time \
        FROM \
            recipe \
        ORDER BY \
            RANDOM() \
        LIMIT \
            1"
    result = db.session.execute(sql)
    return result.fetchone()

def add_recipe(recipe_name, passive_time, active_time, recipe_description, \
    userprofile_id, ingredient_list):
    i_qts = ingredient_list[0]
    i_units = ingredient_list[1]
    i_names = ingredient_list[2]
    current_timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")

    recipe_insert = "INSERT INTO recipe \
            (recipe_name, passive_time, active_time, \
            recipe_description, userprofile_id, created_at) \
        VALUES \
            (:recipe_name, :passive_time, :active_time, \
            :recipe_description, :userprofile_id, :current_timestamp) \
        RETURNING id"
    result = db.session.execute(recipe_insert, \
        {"recipe_name":recipe_name, "passive_time":passive_time, \
        "active_time":active_time, "recipe_description":recipe_description, \
        "userprofile_id":userprofile_id, "current_timestamp":current_timestamp})

    recipe_id = result.fetchone()[0]
    
    ingredient_insert = "INSERT INTO ingredient \
        (ingredient_name) \
        VALUES \
            (unnest(:i_names)) \
        ON CONFLICT DO NOTHING"
    db.session.execute(ingredient_insert, {"i_names":i_names})
    
    recipeingredient_insert = "WITH ingredients AS (\
            SELECT id \
            FROM ingredient \
            WHERE ingredient_name = ANY(:i_names)\
        ), \
        units AS (\
            SELECT * FROM unnest(:i_units) AS unit\
        ), \
        quantities AS (\
            SELECT * FROM unnest(:i_qts) AS quantity\
        ), \
        recipe1 AS (\
            SELECT * FROM unnest(ARRAY[:recipe_id]) AS id\
        ) \
        INSERT INTO recipeingredient \
            (recipe_id, ingredient_id, unit, quantity) \
        SELECT \
            r.id, i.id, u.unit, q.quantity \
        FROM \
            recipe1 r, ingredients i, units u, quantities q \
        WHERE \
            r.id = :recipe_id  \
        "
    db.session.execute(recipeingredient_insert, {"i_names":i_names, \
        "i_units":i_units, "i_qts":i_qts, "recipe_id":recipe_id})    
    db.session.commit()
    return True