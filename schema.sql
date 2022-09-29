CREATE TABLE userprofile (
    id SERIAL PRIMARY KEY,
    userprofile_name TEXT,
    passhash TEXT
);
CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    recipe_name TEXT,
    passive_time INTERVAL,
    active_time INTERVAL,
    recipe_description TEXT,
    created_at TIMESTAMP,
    userprofile_id INTEGER REFERENCES userprofile(id)
);
CREATE TABLE ingredient (
    id SERIAL PRIMARY KEY,
    ingredient_name TEXT UNIQUE
);
CREATE TABLE recipeingredient (
    recipe_id INTEGER REFERENCES recipe,
    ingredient_id INTEGER REFERENCES ingredient,
    unit TEXT,
    quantity FLOAT
);
CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    content TEXT,
    sent_at TIMESTAMP,
    userprofile_id INTEGER REFERENCES userprofile,
    recipe_id INTEGER REFERENCES recipe
);