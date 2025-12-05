from flask import Blueprint, redirect, render_template, url_for, current_app as app
from flask_login import current_user, login_user, login_required
from forms import LoginForm, SearchForm, AddProductForm, EditProductForm, AddCarouselForm, EditCarouselForm

import os
from models import db, User, Product, Carousel
from forms import LoginForm
from utils import allowed_file, unique_filename

admin_bp = Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")

@admin_bp.route("/", methods=["GET", "POST"])
def admin():
    form = LoginForm()
    error = None
    if current_user.is_authenticated:
        return redirect(url_for("admin.admin_dashboard"))

    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("admin.admin_dashboard"))
        else:
            error = "Невірний логін або пароль"

    return render_template("admin.html", error=error, form=form)

@admin_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    form = SearchForm()
    filtered_products = db.session.query(Product)
    if form.validate_on_submit() and form.targetValue.data:
        search_term = f"%{form.targetValue.data.lower()}%"
        filtered_products = filtered_products.filter(Product.searchField.like(search_term))

    return render_template("admin_dashboard.html", products=filtered_products, admin_name=current_user.username, form=form)


@admin_bp.route("/admins", methods=["GET", "POST"])
@login_required
def admin_list():
    form = SearchForm()
    filtered_admins = db.session.query(User)
    if form.validate_on_submit() and form.targetValue.data:
        search_term = f"%{form.targetValue.data.lower()}%"
        filtered_admins = filtered_admins.filter(User.searchField.like(search_term))

    return render_template("admin_dashboard_admins.html", admin_name=current_user.username, admins=filtered_admins, form=form)


@admin_bp.route("/add_product", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template("add_product.html", form=form, error=None)


@admin_bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("edit_product.html", product=product, form=form)


@admin_bp.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], product.img))
    except:
        pass
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/carousel", methods=["GET", "POST"])
@login_required
def admin_carousel():
    carousel_items = db.session.query(Carousel)
    return render_template("admin_carousel.html", admin_name=current_user.username, carousel_items=carousel_items)


@admin_bp.route("/add_carousel_item", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_carousel"))

    return render_template("add_carousel_item.html", form=form, error=None)


@admin_bp.route("/carousel/edit/<int:item_id>", methods=["GET", "POST"])
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
        return redirect(url_for("admin.admin_carousel"))

    return render_template("edit_carousel.html", item=item, form=form)


# Видалення слайду каруселі
@admin_bp.route("/carousel/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_carousel_item(item_id):
    item = db.session.get(Carousel, item_id)
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], item.img))
    except:
        pass
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin.admin_carousel"))