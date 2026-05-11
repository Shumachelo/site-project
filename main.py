from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort, Api
from forms.balance import BalanceForm
from data.lots import Lots
from forms.login_register import RegisterForm, LoginForm
from forms.lot import LotForm
from flask import flash
from data import db_session
from data.users import User
from data.users_api import UsersListResource, UsersResource
from data.lots_api import LotsResource, LotsListResource

app = Flask(__name__)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    lots = db_sess.query(Lots).all()
    return render_template('lots.html', lots=lots)


@app.route('/add_lot', methods=['GET', 'POST'])
@login_required
def add_lot():
    form = LotForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        lot = Lots(
            owner_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            condition=form.condition.data,
            minimal_cost=form.minimal_cost.data,
            minimum_premium=form.minimum_premium.data,
            curr_cost=form.minimal_cost.data
        )

        db_sess.add(lot)
        db_sess.commit()
        db_sess.close()

        return redirect('/')

    return render_template('add_lot.html', title='Добавление лота', form=form)

@app.route('/lot_page/<int:id>')
def lot_page(id):
    db_sess = db_session.create_session()
    lot = db_sess.query(Lots).filter(Lots.id == id).first()
    if not lot:
        abort(404)
    return render_template('lot_page.html', lot=lot)

@app.route('/lot/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lot(id):
    form = LotForm()
    db_sess = db_session.create_session()

    lot = db_sess.query(Lots).filter(Lots.id == id).first()
    if not lot or not (current_user.id == lot.owner_id or current_user.id == 1):
        abort(404)

    if request.method == 'GET':
        form.name.data = lot.name
        form.description.data = lot.description
        form.condition.data = lot.condition
        form.minimal_cost.data = lot.minimal_cost
        form.minimum_premium.data = lot.minimum_premium
        form.is_selled.data = lot.is_selled

    if form.validate_on_submit():
        lot.name = form.name.data
        lot.description = form.description.data
        lot.condition = form.condition.data
        lot.minimal_cost = form.minimal_cost.data
        lot.minimum_premium = form.minimum_premium.data
        lot.is_selled = form.is_selled.data

        db_sess.commit()
        db_sess.close()
        return redirect('/')

    return render_template('edit_lot.html', title='Редактирование лота', form=form)

@app.route('/lot_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_lot(id):
    db_sess = db_session.create_session()
    lot = db_sess.query(Lots).filter(Lots.id == id).first()

    if not lot or not (current_user.id == lot.owner_id or current_user.id == 1):
        abort(404)

    db_sess.delete(lot)
    db_sess.commit()
    db_sess.close()

    return redirect('/')

@app.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    form = BalanceForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.get(User, current_user.id)

        if form.action.data == 'deposit':
            user.balance += form.amount.data
            db_sess.commit()
            flash(f"Баланс пополнен на {form.amount.data} ₽", "success")
        else:
            if user.balance < form.amount.data:
                flash("Недостаточно средств", "danger")
            else:
                user.balance -= form.amount.data
                db_sess.commit()
                flash(f"Выведено {form.amount.data} ₽", "success")

        return redirect('/balance')

    return render_template('balance.html', title='Баланс', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.rep_pas.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже существует")

        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/auction.db")
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>') # API для пользователей

    api.add_resource(LotsListResource, '/api/lots')
    api.add_resource(LotsResource, '/api/lots/<int:lot_id>') # API для лотов

    app.run(host='127.0.0.1', port=8080)
