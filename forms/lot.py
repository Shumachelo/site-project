from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class LotForm(FlaskForm):
    name = StringField('Название лота', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    condition = StringField('Состояние', validators=[DataRequired()])
    minimal_cost = IntegerField('Минимальная цена', validators=[DataRequired()])
    minimum_premium = IntegerField('Минимальная надбавка', validators=[DataRequired()])
    is_selled = BooleanField('Продан')
    submit = SubmitField('Сохранить')