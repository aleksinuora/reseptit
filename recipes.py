from db import db

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
    user_id, ingredient_list):
    i_qts = []
    i_units = []
    i_names = []
    for row in ingredient_list:
        i_qts.append(row[0])
        i_units.append(row[1])
        i_names.append(row[2])

    recipe_insert = "INSERT INTO recipe \
            (recipe_name, passive_time, active_time, \
            recipe_description, user_id, created_at) \
        VALUES \
            (:recipe_name, :passive_time, :active_time, \
            :recipe_description, :user_id, :CURRENT_TIMESTAMP) \
        RETURNING id"
    result = db.session.execute(recipe_insert, \
        {"recipe_name":recipe_name, "passive_time":passive_time, \
        "active_time":active_time, "recipe_description":recipe_description, \
        "user_id":user_id})

    recipe_id = result.fetchone()[0]
    
    ingredient_insert = "INSERT INTO ingredient \
        (ingredient_name) \
        VALUES \
            (unnest(ARRAY:i_names)) \
        ON CONFLICT DO NOTHING"
    db.session.execute(ingredient_insert, {"i_names":i_names})
    
    recipeingredient_insert = "WITH ingredients AS (\
            SELECT id \
            FROM ingredient \
            AS ingredient_id \
            WHERE ingredient_name = ANY(ARRAY:i_names)\
        ), \
        units AS (\
            SELECT * FROM unnest(ARRAY:i_units)\
        ), \
        quantities AS (\
            SELECT * FROM unnest(ARRAY:i_qts)\
        ), \
        recipe AS (\
            SELECT * FROM unnest(ARRAY[:recipe_id]) AS recipe_id \
        ), \
        INSERT INTO recipeingredient \
            (recipe_id, ingredient_id, unit, quantity) \
        SELECT \
            r.recipe_id, i.ingredient_id, u.unit, q.quantity \
        FROM \
            recipe r, ingredients i, units u, quantities q \
        "
    db.session.execute(recipeingredient_insert, {"i_names":i_names, \
        "i_units":i_units, "i_qts":i_qts, "recipe_id":recipe_id})