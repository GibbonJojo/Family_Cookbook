from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SelectField, RadioField, TextAreaField, PasswordField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired


class RecipeForm(FlaskForm):
    name = StringField('Rezeptname', validators=[InputRequired()], render_kw={"class": "form-control"})
    tags = StringField('Tags', render_kw={"placeholder": "Tags mit Komma trennen", "class": "form-control"})
    category = SelectField('Kategorie', render_kw={"class":"browser-default custom-select"}, choices=[('Frühstück', 'Frühstück'), ('Hauptspeisen', 'Hauptspeise'), ('Salate', 'Salat'), ('Suppen', 'Suppe'), ('Vorspeisen', 'Vorspeise'), ('Dessert', 'Dessert'), ('Backen', 'Backen'), ('Getränke', 'Getränk')])
    type = RadioField('Ernährungsweise', validators=[InputRequired()], choices=[('Vegetarisch', 'Vegetarisch'), ('Vegan', 'Vegan'), ('Fisch', 'Fisch'), ('Fleisch', 'Fleisch')])
    picture = FileField('Bild hochladen', render_kw={"class": "custom-file-input", "id": "input"})

    prep_time = IntegerField("Ungefähre Zubereitungszeit (in min)", validators=[InputRequired()], render_kw={"class": "form-control"})

    # ingredients
    ingreds = TextAreaField("Zutaten", render_kw={"rows": "20", "cols": 15, "placeholder": """Zutaten. Z.B:
200 g Mehl
100 mL Wasser"""}, validators=[InputRequired()])

    recipe = TextAreaField("Rezept", render_kw={"rows": "20", "cols": 55, "placeholder": """Rezept. Z.B:
zusammen mit
mischen und..."""}, validators=[InputRequired()])


class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    valid = StringField('Zugangstoken', validators=[InputRequired()])
