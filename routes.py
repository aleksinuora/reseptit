from app import app
from flask import render_template, request, redirect
import recipes
from utilities.form_parser import parse_recipe_form

@app.route("/")
def index():
    recipe = recipes.get_random_recipe()
    id = recipe[0]
    name = recipe[1]
    passiveTime = recipe[2]
    activeTime = recipe[3]
    return render_template("index.html", id=id, name=name, \
        passiveTime=passiveTime, activeTime=activeTime)

@app.route("/recipe", methods=["GET"])
def recipe():
    id = request.args.get("id", None)
    recipe = recipes.get_recipe(id)
    recipeHead = recipe[0]
    name = recipeHead[0]
    passiveTime = recipeHead[1]
    activeTime = recipeHead[2]
    description = recipeHead[3]
    ingredientList = []
    for row in recipe:
        ingredient = (row[5], row[6], row[7])
        ingredientList.append(ingredient)
    return render_template("recipe.html", name=name, \
        passiveTime=passiveTime, activeTime=activeTime, \
            description=description, ingredientList=ingredientList)

@app.route("/recipe_form/", methods=["GET", "POST"])
def recipe_form():
    if request.method == "POST":
        if request.form.get("send_recipe") == "Tallenna":
            # todo: POST to database
            recipe = parse_recipe_form(request.form)
            result = recipes.add_recipe(recipe["recipe_name"], \
                recipe["passive_time"], recipe["active_time"], \
                recipe["recipe_description"], 1, \
                recipe["ingredient_list"])
            return render_template("result.html", \
                recipe=recipe, result = result)
                
        elif request.form.get("new_line") == "seuraava raaka-aine":
            print(request.form)
            ingredient_lines = int(request.form["ingredient_lines"]) + 1            
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            ingredient_names = request.form.getlist("ingredient_name")

            return render_template("recipe_form.html", \
                recipe=request.form, \
                ingredient_lines=ingredient_lines, \
                quantities=quantities, \
                units=units, \
                ingredient_names=ingredient_names)

        elif request.form.get("remove_line"):
            target_line_index = int(request.form.get("remove_line"))
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            ingredient_names=request.form.getlist("ingredient_name")
            del quantities[target_line_index]
            del units[target_line_index]
            del ingredient_names[target_line_index]

            return render_template("recipe_form.html", \
                recipe=request.form, \
                ingredient_lines=len(ingredient_names), \
                quantities=quantities, \
                units=units, \
                ingredient_names=ingredient_names)

    elif request.method == "GET":
        return render_template("recipe_form.html", \
            recipe=[], quantities=[], units=[], ingredient_names=[])
