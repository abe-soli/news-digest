"""Flask アプリケーションの生成。"""

from flask import Flask

from news_digest.settings import PROJECT_ROOT
from news_digest.web.routes import bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
    )
    app.register_blueprint(bp)
    return app
