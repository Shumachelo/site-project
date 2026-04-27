from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired

class JobForm(FlaskForm):
    job = StringField('Job', validators=[DataRequired()])
    work_size = IntegerField('Work size', validators=[DataRequired()])
    collaborators = StringField('collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Работа завершена')
    submit = SubmitField('Отправить')