import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Lots(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'lots'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True) # имя лота

    description = sqlalchemy.Column(sqlalchemy.String, nullable=True) # описание

    condition = sqlalchemy.Column(sqlalchemy.String, nullable=True) # состояние лота

    minimal_cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True) # минимальная цена

    minimum_premium = sqlalchemy.Column(sqlalchemy.Integer, nullable=True) # минимальная надбавка

    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")) # id собственника товара

    user = orm.relationship("User")

