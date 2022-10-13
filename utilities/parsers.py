import re

def parse_form_to_recipe(form):
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
    words = time.split()
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

def parse_recipe_to_form(recipe):
    active_time = parse_time_reverse(str(recipe[0].active_time))
    passive_time = parse_time_reverse(str(recipe[0].passive_time))
    quantities = []
    units = []
    ingredient_names = []
    for row in recipe:
        quantities.append(row.quantity)
        units.append(row.unit)
        ingredient_names.append(row.ingredient_name)
    recipe_form = {
        "name":recipe[0].recipe_name,
        "active_time":active_time,
        "passive_time":passive_time,
        "quantities": quantities,
        "units": units,
        "ingredient_names": ingredient_names,
        "recipe_description": recipe[0].recipe_description
    }
    return recipe_form

def parse_time_reverse(time):
    if (str(time) == "None"):
        return None
    hours = 0
    if "day" in time:
        days = time.split(" day")[0]
        hours += int(days) * 24
        time = time.split(", ")
        time = time[1:2]
        time = ''.join(time)
    time = time.split(":")
    hours += int(time[0])
    minutes = int(time[1])
    return str(hours) + "t " + str(minutes) + "m"