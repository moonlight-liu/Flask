from flask import url_for, Flask
from markupsafe import escape

# ...
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello"


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
