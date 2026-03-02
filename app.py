from flask import url_for, Flask
from markupsafe import escape

# ...
app = Flask(__name__)


# @app.route("/")
# def hello():
#     return "Hello"


@app.route("/user/<name>")
def user_page(name):
    return f"User: {escape(name)}"


@app.route("/test")
def test_url_for():
    output = f"""
    {url_for("hello")}<br>
    {url_for("user_page", name="greyli")}<br>
    {url_for("user_page", name="peter")}<br>
    {url_for("test_url_for")}<br>
    {url_for("test_url_for", num=2)}<br>
    Test page
    """
    return output


# 虚拟数据 用于渲染主页模版
name1 = "Grey Li"
movies1 = [
    {"title": "My Neighbor Totoro", "year": "1988"},
    {"title": "Dead Poets Society", "year": "1989"},
    {"title": "A Perfect World", "year": "1993"},
    {"title": "Leon", "year": "1994"},
    {"title": "Mahjong", "year": "1996"},
    {"title": "Swallowtail Butterfly", "year": "1996"},
    {"title": "King of Comedy", "year": "1999"},
    {"title": "Devils on the Doorstep", "year": "1999"},
    {"title": "WALL-E", "year": "2008"},
    {"title": "The Pork of Music", "year": "2012"},
]

from flask import Flask, render_template

# ...


@app.route("/")
def index():
    return render_template("index.html", name=name1, movies=movies1)
