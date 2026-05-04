from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, NumberRange


class BalanceForm(FlaskForm):
    action = RadioField('Действие', choices=[('deposit', 'Пополнить'), ('withdraw', 'Вывести')], default='deposit')
    amount = IntegerField('Сумма', validators=[DataRequired(), NumberRange(min=1, message="Минимум 1 ₽")])
    submit = SubmitField('Применить')