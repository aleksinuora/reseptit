from app import app
from flask import render_template, request, redirect, session, url_for
from os import getenv
import recipes
import login
import users
from utilities.parsers import parse_recipe_form, parse_search

app.secret_key = getenv("SECRET_KEY")

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
    name = recipeHead.recipe_name
    passiveTime = recipeHead.passive_time
    activeTime = recipeHead.active_time
    description = recipeHead.recipe_description
    ingredientList = []
    for row in recipe:
        ingredient = (row.quantity, row.unit, row.ingredient_name)
        ingredientList.append(ingredient)
    submitter = users.get_username(recipeHead.userprofile_id)
    created_at = recipeHead.created_at
    editing_rights = session.get("username") == "admin" \
        or session.get("username") == submitter

    return render_template("recipe.html", name=name, \
        passiveTime=passiveTime, activeTime=activeTime, \
            description=description, ingredientList=ingredientList, \
            submitter=submitter, editing_rights=editing_rights, \
            created_at=created_at, recipe_id=id)

@app.route("/recipe_form/", methods=["GET", "POST"])
def recipe_form():
    if request.method == "POST":
        if request.form.get("send_recipe") == "Tallenna":
            user_id = users.find_user(session["username"])[0]
            recipe = parse_recipe_form(request.form)
            result = recipes.add_recipe(recipe["recipe_name"], \
                recipe["passive_time"], recipe["active_time"], \
                recipe["recipe_description"], user_id, \
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

@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form["username"]
    password = request.form["password"]
    if login.check_login(username, password):
        session["username"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new_user_form", methods=["GET", "POST"])
def new_user_form():
    if request.method == "GET":
        return render_template("new_user_form.html")
    elif request.method == "POST":
        if users.find_user(request.form.get("username")):
            return render_template("new_user_form.html")
        users.add_user(request.form.get("username"), \
            request.form.get("password"))
        return redirect("/")

@app.route("/delete_recipe", methods=["POST"])
def delete_recipe():
    if request.form.get("delete_button"):
        recipes.remove_recipe(request.form.get("delete_button"), \
            user=session["username"])
        return redirect("/")
    recipe_id = request.form.get("delete_button")
    return redirect(url_for("recipe", id=recipe_id))

@app.route("/browse_recipes", methods=["GET", "POST"])
def browse_recipes():
    if request.method == "GET":
        recipe_list = recipes.get_all_recipes()
        return render_template("browse_recipes.html", recipes=recipe_list)
    if request.method == "POST":
        terms = request.form.getlist("terms")
        term_types = request.form.getlist("term_types")
        term_line_count = int(request.form.get("term_line_count"))
        recipe_name = request.form.get("recipe_name", "")
        if request.form.get("submit_search") == "Hae":
            recipe_list = recipes.get_match_all(parse_search(request.form))
            return render_template("browse_recipes.html", \
                terms=terms, term_line_count=term_line_count, \
                recipe_name=recipe_name, term_types=term_types, \
                recipes=recipe_list)
        elif request.form.get("new_line") == "lisää hakuehto":
            term_line_count += 1             
        elif request.form.get("remove_line"):
            target_line_index = int(request.form.get("remove_line"))
            del terms[target_line_index]
            term_line_count += -1
        return render_template("browse_recipes.html", terms=terms, \
            term_line_count=term_line_count, recipe_name=recipe_name, \
            term_types=term_types)

@app.route("/user")
def user():
    username = request.args.get("username", None)
    user_recipes = recipes.get_match_all({"user":username})
    user_rights = username == session.get("username", None) or \
        session.get("username") == "admin"
    return render_template("user.html", user_rights=user_rights, \
        username=username, recipes=user_recipes)

@app.route("/delete_user", methods=["POST"])
def delete_user():
    username = request.args.get("username")
    session_user = session.get("username")
    user_rights = username == session_user or \
        session_user == "admin"
    if user_rights:
        print("HALOO ", session["username"])
        users.delete_user(username, user=session_user)
    if session.get("username") != "admin":
        return redirect("/logout")
    return redirect("/") 