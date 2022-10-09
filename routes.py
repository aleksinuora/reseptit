from app import app
from flask import render_template, request, redirect, session, url_for
from os import getenv
import recipes
import login
import users
import comments
from utilities.parsers import parse_recipe_form, parse_search

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    recipe = recipes.get_random_recipe()
    id = recipe.id
    name = recipe.recipe_name
    passiveTime = recipe.passive_time
    activeTime = recipe.active_time
    return render_template("index.html", id=id, name=name, \
        passiveTime=passiveTime, activeTime=activeTime)

@app.route("/recipe", methods=["GET", "POST"])
def recipe():
    recipe_id = request.args.get("recipe_id", None)
    recipe = recipes.get_recipe(recipe_id)
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
    comment_to_edit = None
    editing_rights = session.get("username") == "admin" \
        or session.get("username") == submitter    
    if request.method == "POST":
        if (request.form.get("remove_comment") != None):
            comments.delete_comment(request.form.get("remove_comment"))
        if request.form.get("send_comment"):
            user_id = users.find_user(session.get("username")).id
            content = request.form.get("new_comment_text")
            comments.send_recipe_comment(content, user_id, recipe_id)
        if (request.form.get("edit_comment") != None):
            comment_id = request.form.get("edit_comment")
            comment_content = request.form.get("comment_content")
            recipe_id = request.form.get("recipe_id")
            comment_to_edit = {
                "id":comment_id,
                "content":comment_content,
                "recipe_id":recipe_id
                }
        if (request.form.get("save_edit") == "Tallenna"):
            comments.edit_comment(request.form.get("comment_to_edit_id"), \
                request.form.get("new_comment_text"))
    recipe_comments = comments.get_recipe_comments(recipe_id)
    return render_template("recipe.html", name=name, \
        passiveTime=passiveTime, activeTime=activeTime, \
            description=description, ingredientList=ingredientList, \
            submitter=submitter, editing_rights=editing_rights, \
            created_at=created_at, recipe_id=recipe_id, \
            comments=recipe_comments, comment_to_edit=comment_to_edit)

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

@app.route("/login", methods=["GET", "POST"])
def handle_login():
    if request.method == "GET":
        return render_template("login_element.html")
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

@app.route("/user", methods=["GET", "POST"])
def user():
    username = request.args.get("username", None)
    user_recipes = recipes.get_match_all({"user":username})
    recipe_comments = None
    user_rights = username == session.get("username", None) or \
        session.get("username") == "admin"
    if request.method == "POST":
        if request.form.get("show_comments"):
            recipe_comments = comments.get_user_comments(username)
    return render_template("user.html", user_rights=user_rights, \
        username=username, recipes=user_recipes, comments=recipe_comments)

@app.route("/delete_user", methods=["POST"])
def delete_user():
    username = request.args.get("username")
    session_user = session.get("username")
    user_rights = username == session_user or \
        session_user == "admin"
    if user_rights:
        users.delete_user(username, user=session_user)
    if session.get("username") != "admin":
        return redirect("/logout")
    return redirect("/") 