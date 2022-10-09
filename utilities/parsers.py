import re

def parse_recipe_form(form):
    recipe_name = form.get("name")
    passive_time = form.get("passive_time")
    if passive_time:
        passive_time = parse_time(passive_time)
    active_time = form.get("active_time")
    if active_time:
        active_time = parse_time(active_time)
    recipe_description = form.get("recipe_description")
    qt_strings = form.getlist("quantity")
    qt_list = []
    for value in qt_strings:
        qt_list.append(float(value))
    unit_list = form.getlist("unit")
    ingredient_name_list = form.getlist("ingredient_name")
    ingredient_list = [qt_list, unit_list, ingredient_name_list]
    values = {
        'recipe_name': recipe_name,
        'passive_time': passive_time,
        'active_time': active_time,
        'recipe_description': recipe_description,
        'ingredient_list': ingredient_list
    }
    return values
    


def parse_time(time):
    words = str.split(time)
    hours = words[0][:-1]
    minutes = words[1][:-1]
    time = ''
    if re.match(r"[1-9]+[0-9]*", hours):
        time = hours + ' hours '
    time = time + minutes + ' minutes'
    return time

def parse_search(form):
    terms = form.getlist("terms")
    term_types = form.getlist("term_types")
    ingredients = list()
    user = ""
    for i in range (len(terms)):
        if term_types[i] == "ingredients":
            ingredients.append(terms[i])
        elif term_types[i] == "user":
            user = terms[i]
    search_terms = {
        "recipe_name": form.get("recipe_name", ""),
        "ingredients": ingredients,
        "user": user
    }
    return search_terms
