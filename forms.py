from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField
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

class EditProductForm(FlaskForm):
    name = StringField("Назва продукту", validators=[DataRequired()])
    desc = TextAreaField("Опис", validators=[DataRequired()])
    file = FileField("Зображення")
    submit = SubmitField("Додати")

class AddCarouselForm(FlaskForm):
    file = FileField("Зображення", validators=[DataRequired()])
    title = StringField("Заголовок")
    desc = TextAreaField("Опис")
    text_position = SelectField("Позиція тексту", choices=[('left', 'Зліва'), ('right', 'Справа'), ('center', 'По центру'), ('none', 'Без тексту')])
    button_text = StringField("Текст кнопки")
    button_link = StringField("Посилання кнопки")
    submit = SubmitField("Додати слайд")
