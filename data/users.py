import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
        self.second_hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True) # имя пользователя

    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True) # его почта

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True) # пароль

    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now) # дата создания

    balance = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True)

    lots = orm.relationship("Lots", back_populates='user') # связь с другой бд