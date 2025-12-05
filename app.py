from flask import Flask
from flask_login import LoginManager
from models import db, User

from blueprints.main.main_bp import main_bp
from blueprints.admin.admin_bp import admin_bp
from blueprints.error.pageNotFound import error


app = Flask(__name__)
app.secret_key = "SayGex"  # Для сесій

UPLOAD_FOLDER = "static/img"  # де будуть зберігатися завантажені файли
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# -------------------- Routes -------------------- #


app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(error)


# -------------------- Run -------------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
