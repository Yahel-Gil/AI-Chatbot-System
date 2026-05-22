from flask import Blueprint, render_template

# Create about blueprint:
about_blueprint = Blueprint("about_controller", __name__)

# About route:
@about_blueprint.route("/about")
def about():
    return render_template("pages/about.html", active = "about")