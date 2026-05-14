from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed


class LotForm(FlaskForm):
    name = StringField('Название лота', validators=[DataRequired()])
    media = FileField('Выберите медиа файл', validators=[FileRequired(),
                                                         FileAllowed(['jpg', 'png', 'mp4', 'webm'],
                                                                     'Только фото или видео!')])
    description = TextAreaField('Описание', validators=[DataRequired()])
    condition = StringField('Состояние', validators=[DataRequired()])
    minimal_cost = IntegerField('Минимальная цена', validators=[DataRequired()])
    minimum_premium = IntegerField('Минимальная надбавка', validators=[DataRequired()])
    is_selled = BooleanField('Продан')
    submit = SubmitField('Сохранить')


class EditLotForm(FlaskForm):
    name = StringField('Название лота', validators=[DataRequired()])
    media = FileField('Выберите медиа файл', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'mp4', 'webm'], 'Только фото или видео!')
    ])
    description = TextAreaField('Описание', validators=[DataRequired()])
    condition = StringField('Состояние', validators=[DataRequired()])
    minimal_cost = IntegerField('Минимальная цена', validators=[DataRequired()])
    minimum_premium = IntegerField('Минимальная надбавка', validators=[DataRequired()])
    is_selled = BooleanField('Продан')
    submit = SubmitField('Сохранить')