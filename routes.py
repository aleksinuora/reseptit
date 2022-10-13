from app import app
from flask import render_template, request, redirect, session, url_for, abort
from os import getenv
import recipes
import login
from users import get_username, get_users, find_user, add_user, delete_user
import comments
from utilities.parsers import parse_form_to_recipe, parse_search, parse_recipe_to_form, parse_time_reverse
from werkzeug.datastructures import ImmutableMultiDict
import collections
import secrets

app.secret_key = getenv("SECRET_KEY")

# Testing certain functions
@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        params = {
            "eka":1,
            "toka":2,
        }
        return render_template("test.html", params=params)
    elif request.method == "POST":
        print(request.form)
        params = dict(request.form)
        print(params)
        del params["lähetä"]
        print(params)
        return render_template("test.html", params=params)

@app.route("/")
def index():
    recipe = recipes.get_random_recipe()
    passive_time = parse_time_reverse(str(recipe.passive_time))
    active_time = parse_time_reverse(str(recipe.active_time))
    params = {
        "recipe":recipe,
        "recipe_id":recipe.id,
        "recipe_name":recipe.recipe_name,
        "passive_time":passive_time,
        "active_time":active_time
    }
    return render_template("index.html", params=params)

@app.route("/recipe", methods=["GET", "POST"])
def recipe():
    recipe_id = request.args.get("recipe_id", None)
    recipe = recipes.get_recipe(recipe_id)
    recipe_head = recipe[0]
    name = recipe_head.recipe_name
    passive_time = parse_time_reverse(str(recipe_head.passive_time))
    active_time = parse_time_reverse(str(recipe_head.active_time))
    description = recipe_head.recipe_description
    ingredient_list = []
    for row in recipe:
        ingredient = (row.quantity, row.unit, row.ingredient_name)
        ingredient_list.append(ingredient)
    submitter = get_username(recipe_head.userprofile_id)
    created_at = recipe_head.created_at
    comment_to_edit = None
    editing_rights = session.get("username") == "admin" \
        or session.get("username") == submitter
     
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if (request.form.get("remove_comment") != None):
            comments.delete_comment(request.form.get("remove_comment"))
        if request.form.get("send_comment"):
            user_id = find_user(session.get("username")).id
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
        if (request.form.get("save_comment_edit") == "Tallenna"):
            comments.edit_comment(request.form.get("comment_to_edit_id"), \
                request.form.get("new_comment_text"))
    recipe_comments = comments.get_recipe_comments(recipe_id)
    params = {
        "recipe_name":name,
        "passive_time":passive_time,
        "active_time":active_time,
        "recipe_description":description,
        "ingredient_list":ingredient_list,
        "submitter":submitter,
        "editing_rights":editing_rights,
        "created_at":created_at,
        "recipe_id":recipe_id,
        "comment_to_edit":comment_to_edit,
        "comments":recipe_comments
    }
    return render_template("/recipe/recipe.html", params=params)

@app.route("/recipe_form/", methods=["GET", "POST"])
def recipe_form():
    params = {}
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        params = dict(request.form)
        recipe = recipes.get_recipe(params["recipe_id"])
        recipe_form = parse_recipe_to_form(recipe)
        params["recipe"] = recipe_form
        ingredient_lines = len(recipe_form["quantities"])
        if params.get("edit_recipe"):
            return render_template("/recipe/recipe_form.html", \
                recipe=recipe_form, \
                quantities=recipe_form["quantities"], \
                units=recipe_form["units"], \
                ingredient_names=recipe_form["ingredient_names"], \
                editing=True, \
                recipe_id=params["recipe_id"], \
                ingredient_lines=ingredient_lines, \
                params=params)
        if request.form.get("save_recipe_edit"):
            recipe = parse_form_to_recipe(request.form)
            recipe["id"] = request.form.get("save_recipe_edit")
            result = recipes.update_recipe(recipe["id"], recipe["recipe_name"], \
                recipe["passive_time"], recipe["active_time"], \
                recipe["recipe_description"], recipe["ingredient_list"])
            return redirect(url_for("recipe", recipe_id=recipe["id"]))
        if request.form.get("send_recipe"):
            user_id = session["userprofile_id"]
            recipe = parse_form_to_recipe(request.form)
            result = recipes.add_recipe(recipe["recipe_name"], \
                recipe["passive_time"], recipe["active_time"], \
                recipe["recipe_description"], user_id, \
                recipe["ingredient_list"])
            return render_template("result.html", \
                recipe=recipe, result=result)                
        elif request.form.get("new_line") == "seuraava raaka-aine":
            ingredient_lines = int(request.form["ingredient_lines"]) + 1            
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            ingredient_names = request.form.getlist("ingredient_name")            
            return render_template("/recipe/recipe_form.html", \
                editing=request.form.get("editing"), \
                recipe_id=request.form.get("recipe_id"), \
                ingredient_lines=ingredient_lines,
                quantities=quantities,\
                units=units, \
                ingredient_names=ingredient_names, \
                params=params)
        elif request.form.get("remove_line"):
            target_line_index = int(request.form.get("remove_line"))
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")
            ingredient_names=request.form.getlist("ingredient_name")
            del quantities[target_line_index]
            del units[target_line_index]
            del ingredient_names[target_line_index]
            return render_template("/recipe/recipe_form.html", \
                recipe=request.form, \
                ingredient_lines=len(ingredient_names), \
                quantities=quantities, \
                units=units, \
                ingredient_names=ingredient_names, \
                editing=request.form.get("editing"), \
                recipe_id=request.form.get("recipe_id"), \
                params=params)
    elif request.method == "GET":
        params = {
            "recipe":[],
            "quantities":[],
            "units":[],
            "ingredient_names":[]
        }
        return render_template("/recipe/recipe_form.html", params=params)

@app.route("/login", methods=["GET", "POST"])
def handle_login():
    if request.method == "GET":
        return render_template("/user/login.html")
    username = request.form["username"]
    password = request.form["password"]
    user = login.check_login(username, password)
    if user:
        session["username"] = user.userprofile_name
        session["userprofile_id"] = user.id
        session["csrf_token"] = secrets.token_hex(16)
        print(session["csrf_token"])
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["userprofile_id"]
    return redirect("/")

@app.route("/new_user_form", methods=["GET", "POST"])
def new_user_form():
    if request.method == "GET":
        return render_template("/user/new_user_form.html")
    elif request.method == "POST":
        if find_user(request.form.get("username")):
            return render_template("/user/new_user_form.html")
        add_user(request.form.get("username"), \
            request.form.get("password"))
        return redirect("/")

@app.route("/delete_recipe", methods=["POST"])
def delete_recipe():
    if request.form.get("delete_recipe") == "Poista":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        recipes.remove_recipe(request.args.get("recipe_id"), \
            user=session["username"])
        return redirect("/")
    recipe_id = request.args.get("recipe_id")
    return redirect(url_for("recipe", recipe_id=recipe_id))

@app.route("/browse_recipes", methods=["GET", "POST"])
def browse_recipes():
    if request.method == "GET":
        recipe_list = recipes.get_all_recipes()
        return render_template("/recipe/browse_recipes.html", recipes=recipe_list)
    if request.method == "POST":
        terms = request.form.getlist("terms")
        term_types = request.form.getlist("term_types")
        term_line_count = int(request.form.get("term_line_count"))
        recipe_name = request.form.get("recipe_name", "")
        if request.form.get("submit_search") == "Hae":
            recipe_list = recipes.get_match_all(parse_search(request.form))
            return render_template("/recipe/browse_recipes.html", \
                terms=terms, term_line_count=term_line_count, \
                recipe_name=recipe_name, term_types=term_types, \
                recipes=recipe_list)
        elif request.form.get("new_line") == "lisää hakuehto":
            term_line_count += 1             
        elif request.form.get("remove_line"):
            target_line_index = int(request.form.get("remove_line"))
            del terms[target_line_index]
            term_line_count += -1
        return render_template("/recipe/browse_recipes.html", terms=terms, \
            term_line_count=term_line_count, recipe_name=recipe_name, \
            term_types=term_types)

@app.route("/user", methods=["GET", "POST"])
def user():
    username = request.args.get("username", None)
    user_recipes = recipes.get_match_all({"user":username})
    recipe_comments = None
    user_rights = (username == session.get("username", None)) or \
        (session.get("username") == "admin")
    if request.method == "POST":
        if request.form.get("show_comments"):
            recipe_comments = comments.get_user_comments(username)
    return render_template("/user/user.html", user_rights=user_rights, \
        username=username, recipes=user_recipes, comments=recipe_comments)

@app.route("/delete_user", methods=["POST"])
def delete_user():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    username = request.args.get("username")
    session_user = session.get("username")
    user_rights = username == session_user or \
        session_user == "admin"
    if user_rights:
        delete_user(username, user=session_user)
    if session.get("username") != "admin":
        return redirect("/logout")
    return redirect("/")

@app.route("/user_list")
def user_list():
    list_of_users = get_users()
    return render_template("/user/user_list.html", list_of_users=list_of_users)