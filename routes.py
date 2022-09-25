from app import app
from flask import render_template, request
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
