from flask import Blueprint, render_template, redirect, url_for
from flask_login import logout_user
from models import db, Product, Carousel

main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/")
def index():
    carousel_items = db.session.query(Carousel)
    return render_template("index.html", carousel_items=carousel_items)


@main_bp.route("/products")
def products_page():
    products = db.session.query(Product)
    return render_template("products.html", products=products)


@main_bp.route("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin.admin"))