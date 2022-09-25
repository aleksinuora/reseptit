from db import db

def get_recipe(id):
    sql = "SELECT \
            R.recipe_name, R.passive_time, R.active_time, \
            R.recipe_description, R.created_at, \
            Q.quantity, U.unit, I.ingredient_name \
        FROM \
            recipe R, ingredient I, measure_unit U, \
            measure_qt Q, recipeingredient J\
        WHERE \
            R.id=:id \
            AND J.recipe_id=:id \
            AND Q.id=J.measure_qt_id \
            AND U.id=J.measure_unit_id \
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
    recipe_insert = "WITH recipe_insert AS (\
            INSERT INTO recipe \
                (recipe_name, passive_time, active_time, \
                recipe_description, user_id, created_at) \
            VALUES \
                (recipe_name, passive_time, active_time, \
                recipe_description, user_id, CURRENT_TIMESTAMP)\
            RETURNING id\
            ), "
    ingredient_insert = ""
    unit_insert = ""
    quantity_insert = ""
    for row in ingredient_list:
        ingredient_insert.append()
        #todo: sql statement for inserting multiple ingredients