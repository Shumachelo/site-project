import os
from data import db_session, User, UsersResource, UsersListResource, LotsResource, LotsListResource, Lots
from forms import LoginForm, RegisterForm, LotForm, BalanceForm, EditLotForm
from data.bids import Bid
import datetime
from flask_wtf.csrf import generate_csrf

from flask import Flask, render_template, redirect, request, abort, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        return db_sess.get(User, user_id)
    finally:
        db_sess.close()

@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    try:
        lots = db_sess.query(Lots).all()
        return render_template('lots.html', lots=lots, os=os, root_path=app.root_path)
    finally:
        db_sess.close()


@app.route('/add_lot', methods=['GET', 'POST'])
@login_required
def add_lot():
    form = LotForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            file = form.media.data

            lot = Lots(
                owner_id=current_user.id,
                name=form.name.data,
                file=file.filename,
                description=form.description.data,
                condition=form.condition.data,
                minimal_cost=form.minimal_cost.data,
                minimum_premium=form.minimum_premium.data,
                curr_cost=form.minimal_cost.data,
                end_date=form.end_date.data
            )
            db_sess.add(lot)

            os.makedirs('./static/img/lots_img', exist_ok=True)
            file.save(f'./static/img/lots_img/{file.filename}')

            db_sess.commit()

            return redirect('/')
        finally:
            db_sess.close()

    return render_template('add_lot.html', title='Добавление лота', form=form)


@app.route('/lot_page/<int:id>/bid', methods=['POST'])
@login_required
def place_bid(id):
    db_sess = db_session.create_session()

    try:
        lot = db_sess.query(Lots).filter(Lots.id == id).first()

        if not lot or lot.is_selled or lot.owner_id == current_user.id:
            abort(404)

        if lot.end_date and datetime.datetime.now() >= lot.end_date:
            flash('Аукцион уже завершён', 'danger')
            return redirect(f'/lot_page/{id}')

        current_price = lot.curr_cost if lot.curr_cost else lot.minimal_cost
        min_bid = current_price + lot.minimum_premium

        try:
            amount = int(request.form.get('amount', 0))
        except ValueError:
            flash('Некорректная сумма', 'danger')
            return redirect(f'/lot_page/{id}')

        if amount < min_bid:
            flash(f'Минимальная ставка: {min_bid} ₽', 'danger')
            return redirect(f'/lot_page/{id}')

        user = db_sess.get(User, current_user.id)
        if user.balance < amount:
            flash('Недостаточно средств на балансе', 'danger')
            return redirect(f'/lot_page/{id}')

        last_bid = db_sess.query(Bid).filter(Bid.lot_id == id).order_by(Bid.amount.desc()).first()
        if last_bid and last_bid.user_id != current_user.id:
            prev_user = db_sess.get(User, last_bid.user_id)
            prev_user.balance += last_bid.amount

        user.balance -= amount
        lot.curr_cost = amount

        bid = Bid(lot_id=id, user_id=current_user.id, amount=amount)
        db_sess.add(bid)
        db_sess.commit()

        flash(f'Ставка {amount} ₽ принята', 'success')
        return redirect(f'/lot_page/{id}')

    finally:
        db_sess.close()


@app.route('/lot/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lot(id):
    form = EditLotForm()
    db_sess = db_session.create_session()

    try:
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
            file = form.media.data

            lot.name = form.name.data
            lot.description = form.description.data
            lot.condition = form.condition.data
            lot.minimal_cost = form.minimal_cost.data
            lot.minimum_premium = form.minimum_premium.data
            lot.is_selled = form.is_selled.data

            if file is not None:
                lot.file = file.filename
                file.save(f'./static/img/lots_img/{file.filename}')

            db_sess.commit()

            return redirect('/')

        return render_template('edit_lot.html', title='Редактирование лота', form=form, lot=lot)

    finally:
        db_sess.close()


@app.route('/lot_page/<int:id>')
def lot_page(id):
    db_sess = db_session.create_session()

    try:
        lot = db_sess.query(Lots).filter(Lots.id == id).first()
        if not lot:
            abort(404)

        if lot.end_date and datetime.datetime.now() >= lot.end_date and not lot.is_selled:
            lot.is_selled = True
            db_sess.commit()

        return render_template('lot_page.html', lot=lot, csrf_tok=generate_csrf())

    finally:
        db_sess.close()


@app.route('/lot_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_lot(id):
    db_sess = db_session.create_session()

    try:
        lot = db_sess.query(Lots).filter(Lots.id == id).first()

        if not lot or not (current_user.id == lot.owner_id or current_user.id == 1):
            abort(404)

        os.remove('./static/img/lots_img/' + lot.file)

        db_sess.delete(lot)
        db_sess.commit()

        return redirect('/')

    finally:
        db_sess.close()


@app.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    form = BalanceForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        try:
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

        finally:
            db_sess.close()

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

        try:
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

        finally:
            db_sess.close()

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        try:
            user = db_sess.query(User).filter(User.email == form.email.data).first()

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")

            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)

        finally:
            db_sess.close()

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

api.add_resource(UsersListResource, '/api/users')
api.add_resource(UsersResource, '/api/users/<int:user_id>')
api.add_resource(LotsListResource, '/api/lots')
api.add_resource(LotsResource, '/api/lots/<int:lot_id>')

if __name__ == '__main__':
    db_session.global_init("db/auction.db")
    app.run(host='127.0.0.1', port=8080, debug=True)