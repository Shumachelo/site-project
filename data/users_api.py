from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify
from data.users import User
from forms.parser import parser_for_users
from data import db_session

app = Flask(__name__)
api = Api(app)


def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        return jsonify({'user': user.to_dict(
            only=('name', 'email', 'balance', 'modified_date'))})

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'email', 'balance', 'modified_date')) for item in users]})

    def post(self):
        args = parser_for_users.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            email=args['email'],
        )
        user.set_password(args['hashed_password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})