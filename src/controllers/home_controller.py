from flask import Blueprint, render_template

home_blueprint = Blueprint("home_controller", __name__)

# Render the single-page chat interface (Home Page):
@home_blueprint.route("/")
@home_blueprint.route("/home")
def home():
    return render_template("pages/home.html", active="home")