from flask import Flask, render_template, redirect, url_for, abort
from forms import LoginForm, SearchForm, AddProductForm, EditProductForm, AddCarouselForm, EditCarouselForm
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from models import db, User, Product, Carousel
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "SayGex"  # Для сесій

UPLOAD_FOLDER = "static/img"  # де будуть зберігатися завантажені файли
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_filename(filename):
    ext = filename.rsplit('.', 1)[1]
    return secure_filename(f"{uuid4()}.{ext}")


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Список користувачів
admins = [
    # {
    #     "username": "admin",
    #     "password": "12345",
    #     "name": "Головний Адмін",
    #     "email": "admin@example.com",
    # },
    # {
    #     "username": "root",
    #     "password": "qwerty",
    #     "name": "Супер Адмін",
    #     "email": "root@example.com",
    # },
]

# Список продуктів
products = [
    # {
    #     "id": 1,
    #     "name": "Atlas",
    #     "desc": "Гуманоїдний робот для мобільності та досліджень.",
    #     "img": "hero1.png",
    # },
    # {
    #     "id": 2,
    #     "name": "Spot",
    #     "desc": "Робот-собака для промислових і оборонних задач.",
    #     "img": "hero2.png",
    # },
    # {
    #     "id": 3,
    #     "name": "Handle",
    #     "desc": "Робот для складів та логістики.",
    #     "img": "hero3.png",
    # },
]

# Карусель
carousel_items = [
    # {
    #     "id": 1,
    #     "img": "su-27.jpg",
    #     "title": "Технології для нашої авіації",
    #     "desc": "Технології, з якими 'Привид Києва' став Легендою.",
    #     "text_position": "right",
    #     "button_text": "Переглянути продукцію",
    #     "button_link": "/products",
    # },
    # {
    #     "id": 2,
    #     "img": "fpv.jpeg",
    #     "title": "FPV — дрони",
    #     "desc": "Зброя, що змінила сучасну війну.",
    #     "text_position": "left",
    #     "button_text": "Переглянути продукцію",
    #     "button_link": "/products",
    # },
    # {
    #     "id": 3,
    #     "img": "ssu2.jpg",
    #     "title": "Якісне спорядження",
    #     "desc": "Комфорт та безпека.",
    #     "text_position": "center",
    #     "button_text": "Переглянути продукцію",
    #     "button_link": "/products",
    # },
]

# -------------------- Routes -------------------- #


@app.route("/")
def index():
    carousel_items = db.session.query(Carousel)
    return render_template("index.html", carousel_items=carousel_items)


@app.route("/products")
def products_page():
    products = db.session.query(Product)
    return render_template("products.html", products=products)


@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    form = LoginForm()
    error = None
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Невірний логін або пароль"

    return render_template("admin.html", error=error, form=form)


@app.route("/admin/dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    form = SearchForm()
    filtered_products = db.session.query(Product)
    if form.validate_on_submit() and form.targetValue.data:
        search_term = f"%{form.targetValue.data.lower()}%"
        filtered_products = filtered_products.filter(Product.searchField.like(search_term))

    return render_template("admin_dashboard.html", products=filtered_products, admin_name=current_user.username, form=form)


@app.route("/admin/admins", methods=["GET", "POST"])
@login_required
def admin_list():
    form = SearchForm()
    filtered_admins = db.session.query(User)
    if form.validate_on_submit() and form.targetValue.data:
        search_term = f"%{form.targetValue.data.lower()}%"
        filtered_admins = filtered_admins.filter(User.searchField.like(search_term))

    return render_template("admin_dashboard_admins.html", admin_name=current_user.username, admins=filtered_admins, form=form)


@app.route("/admin/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        file = form.file.data
        if not file or not allowed_file(file.filename):
            return render_template("add_product.html", form=form, error="Невірний тип файлу")

        filename = unique_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        new_product = Product()
        form.populate_obj(new_product)
        new_product.img = filename
        new_product.searchField = f"{new_product.name} {new_product.desc}".lower()
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    
    return render_template("add_product.html", form=form, error=None)


@app.route("/admin/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = EditProductForm(obj=product)
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], product.img))
            filename = unique_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            product.img = filename
            
        form.populate_obj(product)
        product.searchField = f"{product.name} {product.desc}".lower()
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_product.html", product=product, form=form)


@app.route("/admin/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], product.img))
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/carousel", methods=["GET", "POST"])
@login_required
def admin_carousel():
    carousel_items = db.session.query(Carousel)
    return render_template("admin_carousel.html", admin_name=current_user.username, carousel_items=carousel_items)


@app.route("/admin/add_carousel_item", methods=["GET", "POST"])
@login_required
def add_carousel_item():
    form = AddCarouselForm()
    if form.validate_on_submit():
        file = form.file.data
        if not file or not allowed_file(file.filename):
            return render_template("add_carousel_item.html", form=form, error="Невірний тип файлу")

        new_carousel = Carousel()
        form.populate_obj(new_carousel)
        filename = unique_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        new_carousel.img = filename
        if not new_carousel.button_link:
            new_carousel.button_link = "#"

        db.session.add(new_carousel)
        db.session.commit()
        return redirect(url_for("admin_carousel"))

    return render_template("add_carousel_item.html", form=form, error=None)


@app.route("/admin/carousel/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_carousel(item_id):
    item = Carousel.query.get_or_404(item_id)
    form = EditCarouselForm(obj=item)
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], item.img))
            filename = unique_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            item.img = filename

        form.populate_obj(item)
        db.session.commit()
        return redirect(url_for("admin_carousel"))

    return render_template("edit_carousel.html", item=item, form=form)


# Видалення слайду каруселі
@app.route("/admin/carousel/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_carousel_item(item_id):
    item = db.session.get(Carousel, item_id)
    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], item.img))
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin_carousel"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin"))


# -------------------- Run -------------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        for admin in admins:
            if User.query.filter_by(username=admin["username"]).first():
                continue
            new_user = User()
            new_user.username = admin["username"]
            new_user.email = admin["email"]
            new_user.password = admin["password"]
            new_user.name = admin["name"]
            new_user.searchField = f"{admin["name"]} {admin["username"]}".lower()
            db.session.add(new_user)

        for product in products:
            if Product.query.filter_by(name=product["name"]).first():
                continue
            new_product = Product()
            new_product.name = product["name"]
            new_product.desc = product["desc"]
            new_product.img = product["img"]
            new_product.searchField = f"{product["name"]} {product["desc"]}".lower()
            db.session.add(new_product)

        for item in carousel_items:
            if Carousel.query.filter_by(title=item["title"]).first():
                continue
            new_item = Carousel()
            new_item.img = item["img"]
            new_item.title = item["title"]
            new_item.desc = item["desc"]
            new_item.text_position = item["text_position"]
            new_item.button_text = item["button_text"]
            new_item.button_link = item["button_link"]
            db.session.add(new_item)
        db.session.commit()
    app.run(debug=True)
