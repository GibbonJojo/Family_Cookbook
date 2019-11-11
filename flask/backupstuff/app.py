# TODO: Impressum & Contact
# TODO: Picture upload and picture on recipe site
# TODO: Filter for category and type
# TODO: Category tabs in typesite
# TODO: Shared site for category and type
# TODO: Mobile friendly

from flask import Flask, render_template, redirect, session, url_for, request, flash
from flask_pymongo import PyMongo
from flask_bootstrap import Bootstrap
from Forms import RecipeForm, UserForm
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
    # TODO FOR LATER: Display favored recipes
    all_recipes = db.recipes.find(limit=10)

    return render_template("home.html", rec=list(all_recipes))


@app.route("/add/", methods=["GET", "POST"])
@login_required
def add():
    # TODO: Bootstrap WTForms
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
                "picture": None # TODO
            }
            insert_res = db.recipes.insert_one(recipe_doc)
            print(f"{form.name.data}: {insert_res.acknowledged}")

            return redirect(url_for('recipe', id=form.name.data))

    return render_template("add.html", form=form)


@app.route("/login/", methods=["GET", "POST"])
def login():
    # TODO: Bootstrap WTForms
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
    # TODO: Implement sort function
    # TODO: Implement pagination
    recipes = db.recipes.find()
    return render_template("all.html", rec=recipes)


@app.route("/<string:typ>/")
def typ(typ):
    # TODO: Implement sort function
    # TODO: Implement pagination
    recipes = db.recipes.find({"type": typ})
    return render_template("type.html", rec=recipes, typ=typ)


@app.route("/<string:category>/<string:typ>")
def category(category, typ):
    # TODO: Implement sort function
    # TODO: Implement pagination
    # TODO: Implement tabs for types
    if typ == "Alle":
        recipes = db.recipes.find({"category": category})
    else:
        recipes = db.recipes.find({"category": category, "type": typ})

    return render_template("category.html", rec=recipes, category=category, typ=typ)


@app.route("/search/", methods=["GET", "POST"])
def search():

    # TODO: Implement more eloquent search filter (by tags, category and such)
    # TODO: Implement pagination
    search = request.form["search"]
    query = re.compile(search, re.IGNORECASE)

    result = db.recipes.find({"$or": [{"name": query}, {"ingredients": query}, {"tags": query}, {"recipe": query}]})

    return render_template("search.html", result=result, term=search)


@app.route("/recipe/<string:id>")
def recipe(id):
    # TODO: Make recipe editable (implement another route probably)
    # TODO: Favorite button
    recipe = db.recipes.find_one({"name": id})

    return render_template("recipe.html", recipe=recipe)


@app.route("/edit/<string:id>")
def edit(id):
    # TODO: Create edit.html akin to add.html
    recipe = db.recipes.find_one({"name": id})
    return render_template("edit.html", recipe=recipe)


@app.route("/register/")
def register():
    # TODO: Implement temporary key
    form = UserForm()
    if form.validate_on_submit() and form.valid == VALID_TOKEN:
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": sha256_crypt.hash(form.password.data)
        }

        db.users.insert_one(user)
        return redirect(url_for('home'))

    return render_template("register.html", form=form)


@app.route("/profile/")
@login_required
def profile():
    # TODO: implement profile site with editable options (favorites, password, email, created recipes)
    return render_template("profile.html", user=session["username"])


@app.route("/impressum/")
def impressum():
    # TODO: Impressum
    return render_template("impressum.html")


@app.route("/kontakt/")
def kontakt():
    # TODO: Contact
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
