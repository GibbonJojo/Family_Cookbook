
# ! TODO BEFORE PRODUCTION
# TODO: Impressum & Contact
# TODO: Split routes in different files for readability
# TODO: Picture upload and picture on recipe site
# TODO: Shared site for category and type
# TODO: Edit function - NOT WORKING PROPERLY YET
# TODO: Make Edit Route unaccessible
# TODO: "Warenkorb/Einkaufsliste"
# TODO: Dont allow multiple usernames or emails! => Implemented, but have to check if it works

# TODO: Better search function
    # TODO: Filter for category and type
    # TODO: Maybe mongo-query function
# TODO: Category tabs in typesite
# TODO: Mobile friendly
# TODO: Create REST API
# TODO: Favorites
    # TODO: Display Favorites on Home above recently added
# TODO: Delete Button
# TODO: Sort Functions for all recipe sites
# TODO: Pagination for all recipe sites
# TODO: implement profile site with editable options (favorites, password, email, created recipes)
# TODO: If enough traffic - ads for non-registered

from flask import Flask, render_template, redirect, session, url_for, request, flash
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from Forms import RecipeForm, UserForm, Recipe_Edit
from SECRETS import *
from datetime import datetime
from functions import login_required
from passlib.hash import sha256_crypt
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET
app.config["MONGO_URI"] = MDB_URI
db = PyMongo(app).db
Bootstrap(app)


# Make the zip function available in html forms
@app.template_global(name='zip')  # thanks thkang on Stackoverflow
def _zip(*args, **kwargs):  # to not overwrite builtin zip in globals
    return __builtins__.zip(*args, **kwargs)


@app.route("/")
def home():
    all_recipes = db.recipes.find(limit=10)

    return render_template("home.html", rec=list(all_recipes))


@app.route("/add/", methods=["GET", "POST"])
@login_required
def add():
    form = RecipeForm()
    if form.validate_on_submit():
        # check if the recipe name already exists
        if db.recipes.find_one({"name": form.name.data}) is not None:
            flash("Rezeptname gibt es bereits")

        elif ".jpg" not in form.picture.data.filename and ".png" not in form.picture.data.filename:
            flash("Ungültige Bildendung")

        else:

            recipe_doc = {
                "name": form.name.data,
                "ingredients": form.ingreds.data.split("\n"),
                "recipe": form.recipe.data.split("\n"),
                "category": form.category.data,
                "type": form.type.data,
                "tags": form.tags.data.split(", "),
                "date_posted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date_updated": None,
                "picture": None, # TODO
                "creator": session['username']
            }
            insert_res = db.recipes.insert_one(recipe_doc)
            print(f"{form.name.data}: {insert_res.acknowledged}")

            return redirect(url_for('recipe', id=form.name.data))

    return render_template("add.html", form=form)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form['username']
        password = request.form['password']

        userObj = db.users.find_one({"$or": [{"username": user}, {"email": user}]})

        if userObj is not None:
            # password check. Use sha256_crypt
            if sha256_crypt.verify(password, userObj["password"]):
                session['logged_in'] = True
                session['username'] = userObj["username"]
                return redirect(url_for("home"))

            else:
                flash("Ungültiger Username oder Passwort")

        else:
            flash("Ungültiger Username oder Passwort")

    return render_template("login.html")


@app.route("/all/")
def all_rec():
    recipes = db.recipes.find()
    return render_template("all.html", rec=recipes)


@app.route("/<string:typ>/")
def typ(typ):
    recipes = db.recipes.find({"type": typ})
    return render_template("type.html", rec=recipes, typ=typ)


@app.route("/<string:category>/<string:typ>")
def category(category, typ):
    if typ == "Alle":
        recipes = db.recipes.find({"category": category})
    else:
        recipes = db.recipes.find({"category": category, "type": typ})

    return render_template("category.html", rec=recipes, category=category, typ=typ)


@app.route("/search/", methods=["GET", "POST"])
def search():
    search = request.form["search"]
    query = re.compile(search, re.IGNORECASE)

    result = db.recipes.find({"$or": [{"name": query}, {"ingredients": query}, {"tags": query}, {"recipe": query}]})

    return render_template("search.html", result=result, term=search)


@app.route("/recipe/<string:id>")
def recipe(id):
    recipe = db.recipes.find_one({"name": id})

    return render_template("recipe.html", recipe=recipe)


@app.route("/edit/<string:id>")
def edit(id):
    pre_recipe = db.recipes.find_one({"name": id})
    form = Recipe_Edit(pre_recipe)
    return render_template("edit.html", recipe=pre_recipe, form=form)


@app.route("/register/")
def register():
    form = UserForm()
    if form.validate_on_submit() and form.valid == VALID_TOKEN:
        if db.users.find({"username": form.username.data}) is not None and db.users.find({"email": form.email.data}) is not None:
            user = {
                "username": form.username.data,
                "email": form.email.data,
                "password": sha256_crypt.hash(form.password.data)
            }

            db.users.insert_one(user)
            return redirect(url_for('home'))

        else:
            flash("Username oder Email gibt es bereits")

    return render_template("register.html", form=form)


@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html", user=session["username"])


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    recipe = db.recipes.find({"name": id})
    # ! check again for right username!
    return render_template(url_for('home'))


@app.route("/impressum/")
def impressum():
    return render_template("impressum.html")


@app.route("/kontakt/")
def kontakt():
    return render_template("contact.html")


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("Du bist nun ausgeloggt")
    return redirect(url_for("home"))


@app.errorhandler(404)
def error404(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error500(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run()
