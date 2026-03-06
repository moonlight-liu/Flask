from flask import Flask, render_template
from sqlalchemy import select

from .blueprints import auth_bp, main_bp
from .commands import admin, forge, init_database
from .config import config
from .extensions import db, login_manager
from .models import User


def inject_user():
    user = db.session.execute(select(User)).scalar()
    return dict(user=user)


def page_not_found(error):
    return render_template("404.html"), 404


def create_app(config_name="development"):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = (
        "auth.login"  # pyright: ignore[reportAttributeAccessIssue]
    )
    login_manager.login_message = "请先登录"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    app.context_processor(inject_user)
    app.register_error_handler(404, page_not_found)

    app.cli.add_command(init_database)
    app.cli.add_command(forge)
    app.cli.add_command(admin)

    return app
