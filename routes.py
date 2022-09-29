from app import app
from flask import render_template, request, redirect
import recipes

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
            return render_template("result.html", \
                recipe=request.form)
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
        elif request.form.get("remove_line").startswith("poista"):
            target_line = request.form.get("remove_line")
            target_index = int(target_line[slice(6, len(target_line))]) - 1
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            ingredient_names=request.form.getlist("ingredient_name")
            del quantities[target_index]
            del units[target_index]
            del ingredient_names[target_index]
            return render_template("recipe_form.html", \
                recipe=request.form, \
                ingredient_lines=len(ingredient_names), \
                quantities=quantities, \
                units=units, \
                ingredient_names=ingredient_names)
    elif request.method == "GET":
        return render_template("recipe_form.html", \
            recipe=[], quantities=[], units=[], ingredient_names=[])
