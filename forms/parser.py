from flask_restful import reqparse

parser_for_users = reqparse.RequestParser() # аргументы для создания пользователя
parser_for_users.add_argument('name', required=True, type=str)
parser_for_users.add_argument('email', required=True, type=str)
parser_for_users.add_argument('hashed_password', required=True, type=str)

parser_for_lots = reqparse.RequestParser() # аргументы для создания лота
parser_for_lots.add_argument('name', type=str, required=True)
parser_for_lots.add_argument('description', type=str, required=True)
parser_for_lots.add_argument('condition', type=str, required=True)
parser_for_lots.add_argument('minimal_cost', type=int, required=True)
parser_for_lots.add_argument('minimum_premium', type=int, required=True)
parser_for_lots.add_argument('curr_cost', type=int, required=True)
parser_for_lots.add_argument('owner_id', type=int, required=True)
parser_for_lots.add_argument('is_selled', type=bool, required=False, default=False)