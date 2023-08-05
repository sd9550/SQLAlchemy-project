from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, SelectField, IntegerField, validators
from wtforms.validators import DataRequired
import requests
import os

API_KEY = os.environ["API_KEY"]
API_ENDPOINT = "https://api.mobygames.com/v1/games"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///search.db"
app.config["APPLICATION_ROOT"] = "/"
Bootstrap5(app)
db = SQLAlchemy()
db.init_app(app)


# database class
class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    img_url = db.Column(db.String(100), nullable=False)


# form class
class AddForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    search = SubmitField("Search")


# main page
@app.route("/")
def home():
    result = db.session.execute(db.select(Games).order_by(Games.id))
    all_games = result.scalars()
    return render_template("index.html", games=all_games)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    # use API to gather all related title data
    if request.method == "POST":
        g_title = request.form.get("title")

        params = {
            "api_key": API_KEY,
            "title": g_title
        }

        response = requests.get(url=API_ENDPOINT, params=params)
        response.raise_for_status()

        game_data = response.json()["games"]
        number_of_results = len(game_data)

        return render_template("search-results.html", data=game_data, results=number_of_results)

    return render_template("add.html", form=form)


@app.route("/search", methods=["GET", "POST"])
@app.route("/search/<g_title>", methods=["GET", "POST"])
def search(g_title=""):
    game_title = request.args.get("title")
    game_image = request.args.get("img")
    game_description = "placeholder"
    # add item to database if user clicked on it
    new_game = Games(
        title=game_title,
        description=game_description,
        img_url=game_image
    )

    with app.app_context():
        db.session.add(new_game)
        db.session.commit()

    return redirect("/")


@app.route("/delete/<int:g_id>")
def delete(g_id):
    game_to_delete = db.get_or_404(Games, g_id)
    db.session.delete(game_to_delete)
    db.session.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
