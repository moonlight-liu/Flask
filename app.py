from flask import flash, request, url_for, Flask, render_template, redirect
from markupsafe import escape
import os
import sys
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

SQLITE_PREFIX = "sqlite:///" if sys.platform.startswith("win") else "sqlite:////"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"  # 生成随机字符串，作为密钥使用


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = SQLITE_PREFIX + str(
    Path(app.root_path) / "data.db"
)

db = SQLAlchemy(app, model_class=Base)

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from flask_login import UserMixin, login_required, logout_user, login_user, current_user


class User(db.Model, UserMixin):  # 表名将会是 user
    __tablename__ = "user"  # 定义表名称
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键
    name: Mapped[str] = mapped_column(String(20))  # 名字
    username: Mapped[str] = mapped_column(String(20), unique=True)  # 用户名，唯一
    password_hash: Mapped[str] = mapped_column(String(128))  # 密码哈希值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(
            password
        )  # 将密码转换为哈希值并存储在 password_hash 字段中

    def validate_password(self, password):  # 用来验证密码的方法，接受密码作为参数
        return check_password_hash(
            self.password_hash, password
        )  # 将输入的密码与存储的哈希值进行比较，返回布尔值


class Movie(db.Model):  # 表名将会是 movie
    __tablename__ = "movie"
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键
    title: Mapped[str] = mapped_column(String(60))  # 电影标题
    year: Mapped[str] = mapped_column(String(4))  # 电影年份


import click


@app.cli.command("init-db")  # 注册为命令，传入自定义命令名
@click.option("--drop", is_flag=True, help="Create after drop.")  # 设置选项
def init_database(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.")  # 输出提示信息


# @app.route("/")
# def hello():
#     return "Hello"

from sqlalchemy import select, func


@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":  # 判断是否为POST请求
        if not current_user.is_authenticated:  # 如果用户未认证（未登录）
            return redirect(url_for("index"))  # 重定向回主页
        # 获取表单数据
        title = request.form.get("title")  # 电影标题
        year = request.form.get("year")  # 电影年份
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input.")  # 显示错误提示
            return redirect(url_for("index"))  # 重定向回主页
        # 保存数据
        movie = Movie()  # 创建电影记录
        movie.title = title
        movie.year = year
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash("Item created.")  # 显示成功提示
        return redirect(url_for("index"))  # 重定向回主页

    movies = db.session.execute(select(Movie)).scalars().all()  # 获取所有电影记录
    return render_template("index.html", movies=movies)  # 渲染主页模板


@app.cli.command()
def forge():
    """Generate fake data."""
    db.drop_all()
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = "Grey Li"
    movies = [
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

    user = User()
    user.name = name
    user.username = "admin"
    user.set_password("helloflask")
    db.session.add(user)
    for m in movies:
        movie = Movie()
        movie.title = m["title"]
        movie.year = m["year"]
        db.session.add(movie)

    db.session.commit()
    click.echo("Done.")


@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
@login_required  # 登录保护，未登录用户访问会被重定向到登录页面
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)

    if request.method == "POST":  # 处理编辑表单的提交请求
        title = request.form.get("title")
        year = request.form.get("year")

        if title:
            title = title.strip()
        if year:
            year = year.strip()

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash("Invalid input.")
            return redirect(
                url_for("edit", movie_id=movie_id)
            )  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash("Item updated.")
        return redirect(url_for("index"))  # 重定向回主页

    return render_template("edit.html", movie=movie)  # 传入被编辑的电影记录


@app.route("/movie/delete/<int:movie_id>", methods=["POST"])  # 限定只接受 POST 请求
@login_required  # 登录保护，未登录用户访问会被重定向到登录页面
def delete(movie_id):
    movie = db.get_or_404(Movie, movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash("Item deleted.")
    return redirect(url_for("index"))  # 重定向回主页


@app.cli.command()
@click.option("--username", prompt=True, help="The username used to login.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="The password used to login.",
)
def admin(username, password):
    """Create user."""
    db.create_all()

    user = db.session.execute(select(User)).scalar()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo("Creating user...")
        user = User()
        user.username = username
        user.name = "Admin"
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo("Done.")


# 初始化 Flask-Login
from flask_login import LoginManager

login_manager = LoginManager(app)  # 实例化扩展类


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = db.session.get(
        User, int(user_id)
    )  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Invalid input.")
            return redirect(url_for("login"))

        user = db.session.execute(select(User).filter_by(username=username)).scalar()
        # 验证密码是否一致
        if user is not None and user.validate_password(password):
            login_user(user)  # 登入用户
            flash("Login success.")
            return redirect(url_for("index"))  # 重定向到主页

        flash("Invalid username or password.")  # 如果验证失败，显示错误消息
        return redirect(url_for("login"))  # 重定向回登录页面

    return render_template("login.html")


login_manager.login_view = "login"  # pyright: ignore[reportAttributeAccessIssue]
# 设置登录视图端点（默认值为 "login"），当未登录用户访问需要登录的页面时，会被重定向到这个端点
login_manager.login_message = "请先登录"  # 设置登录提示消息


@app.route("/logout")
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash("Goodbye.")
    return redirect(url_for("index"))  # 重定向回首页


# 支持设置用户名字
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        name = request.form.get("name")

        if not name or len(name) > 20:
            flash("Invalid input.")
            return redirect(url_for("settings"))

        current_user.name = name  # 更新当前用户的名字
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = db.session.get(User, current_user.id)
        # user.name = name
        db.session.commit()
        flash("Settings updated.")
        return redirect(url_for("index"))

    return render_template("settings.html")
