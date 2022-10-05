from db import db
import datetime

def get_recipe(id):
    sql = "SELECT \
            R.recipe_name, R.passive_time, R.active_time, \
            R.recipe_description, R.created_at, \
            J.quantity, J.unit, I.ingredient_name, \
            R.userprofile_id, R.created_at \
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

def get_all_recipes():
    sql = "SELECT \
            id, recipe_name \
        FROM \
            recipe \
        GROUP BY \
            id \
        ORDER BY \
            recipe_name ASC, id"
    result = db.session.execute(sql)
    return result.fetchall()

def get_match_all(search_terms):
    filter_string = ""
    if search_terms.get("ingredients", []) != []:
        ingredient_constraints = [(-1,)]
        ingredient_filter_sql = "\
            WITH \
            ingredient_names AS (\
                SELECT * \
                FROM unnest(:ingredients) \
                AS ingredient_names\
            ),    \
            ingredient_ids AS (\
                SELECT DISTINCT \
                    id \
                FROM \
                    ingredient \
                WHERE \
                    ingredient_name = ANY (\
                        SELECT * FROM ingredient_names)\
            ) \
            SELECT DISTINCT \
                recipe_id AS recipe_id\
            FROM \
                recipeingredient \
            WHERE \
                ingredient_id = ANY (\
                    SELECT * FROM ingredient_ids) \
            "
        
        ingredient_result = db.session.execute(ingredient_filter_sql, \
            {"ingredients":search_terms.get("ingredients")}).fetchall()
        if ingredient_result:
            ingredient_constraints = ingredient_result
        for [line] in ingredient_constraints:
            filter_string += " AND id=" + str(line) + " "
  
   
    if search_terms.get("user", "") != "":
        user_constraint = -1
        user_filter_sql = "\
            SELECT id AS userprofile_id\
            FROM userprofile \
            WHERE userprofile_name = :user\
            "
        user_result = db.session.execute(user_filter_sql, \
            {"user":search_terms.get("user")}).fetchone()
        if user_result:
            user_constraint = user_result.userprofile_id
        filter_string += " AND userprofile_id=" + str(user_constraint) + " "

    recipe_name = search_terms.get("recipe_name", "")
    sql = "\
        SELECT \
            id, recipe_name \
        FROM \
            recipe \
        WHERE \
            id = id \
        AND \
            LOWER (recipe_name) LIKE LOWER (Concat(:recipe_name, '%')) " \
        + filter_string + "\
        GROUP BY \
            id \
        ORDER BY \
            recipe_name ASC, id\
        "
    result = db.session.execute(sql, \
        {"recipe_name":search_terms.get("recipe_name", "")})
    return result.fetchall()

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
    
    for i in range (len(i_names)):
        recipeingredient_insert = "WITH i_id AS (\
                SELECT id \
                FROM ingredient \
                WHERE ingredient_name=:ingredient_name\
            )\
            INSERT INTO recipeingredient \
            (recipe_id, ingredient_id, unit, quantity) \
            SELECT :recipe_id, id, :unit, :quantity \
            FROM i_id"
        db.session.execute(recipeingredient_insert, {"ingredient_name":i_names[i], \
            "recipe_id":recipe_id, "unit":i_units[i], "quantity":i_qts[i]})    
    db.session.commit()
    return get_recipe(recipe_id)

def remove_recipe(recipe_id, **kvargs):
    sql = "DELETE FROM recipe WHERE id=:recipe_id"
    db.session.execute(sql, {"recipe_id":recipe_id})

    if kvargs["user"] != "Testaaja":
        db.session.commit()