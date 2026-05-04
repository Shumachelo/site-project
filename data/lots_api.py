from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify
from data.lots import Lots
from forms.parser import parser_for_lots
from data import db_session

app = Flask(__name__)
api = Api(app)


def abort_if_lots_not_found(lot_id):
    session = db_session.create_session()
    lot = session.query(Lots).get(lot_id)
    if not lot:
        abort(404, message=f"lot {lot_id} not found")


class LotsResource(Resource):
    def get(self, lot_id):
        abort_if_lots_not_found(lot_id)
        session = db_session.create_session()
        lot = session.get(Lots, lot_id)
        return jsonify({'lot': lot.to_dict(
            only=('name', 'description', 'condition', 'minimal_cost', 'minimum_premium', 'curr_cost', 'owner_id',
                  'is_selled'))})

    def delete(self, lot_id):
        abort_if_lots_not_found(lot_id)
        session = db_session.create_session()
        lot = session.get(Lots, lot_id)
        session.delete(lot)
        session.commit()
        return jsonify({'success': 'OK'})


class LotsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        lots = session.query(Lots).all()
        return jsonify({'lots': [item.to_dict(
            only=('name', 'description', 'condition', 'minimal_cost', 'minimum_premium', 'curr_cost', 'owner_id',
                  'is_selled')) for item in lots]})

    def post(self):
        args = parser_for_lots.parse_args()
        session = db_session.create_session()
        lot = Lots(
            name=args['name'],
            description=args['description'],
            condition=args['condition'],
            minimal_cost=args['minimal_cost'],
            minimum_premium=args['minimum_premium'],
            curr_cost=args['curr_cost'],
            owner_id=args['owner_id'],
            is_selled=args['is_selled']
        )
        session.add(lot)
        session.commit()
        return jsonify({'id': lot.id})
