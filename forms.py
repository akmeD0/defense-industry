from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Логін", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Увійти")


class SearchForm(FlaskForm):
    targetValue = StringField("Пошук продуктів...")
    submit = SubmitField("Пошук")


class AddProductForm(FlaskForm):
    name = StringField("Назва продукту", validators=[DataRequired()])
    desc = TextAreaField("Опис", validators=[DataRequired()])
    file = FileField("Зображення", validators=[DataRequired()])
    submit = SubmitField("Додати")
