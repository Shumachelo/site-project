from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import reqparse, abort, Api, Resource
from data.lots import Lots
from forms.login_register import RegisterForm, LoginForm
from forms.add_job import JobForm
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


@app.route('/jobs')
@login_required
def show_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Lots).all()
    return render_template('jobs.html', jobs=jobs)


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Lots).all()
    return render_template('jobs.html', jobs=jobs)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        job = Lots(
            team_leader=current_user.id,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data
        )

        db_sess.add(job)
        db_sess.commit()

        return redirect('/jobs')

    return render_template('add_job.html', title='Добавление работы', form=form)


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobForm()
    db_sess = db_session.create_session()

    job = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if not job or not (current_user.id == job.team_leader or current_user.id == 1):
        abort(404)

    if request.method == "GET":
        form.job.data = job.job
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished

    if form.validate_on_submit():
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data

        db_sess.commit()
        return redirect('/jobs')

    return render_template('edit_job.html',
                           title='Редактирование работы',
                           form=form,
                           job_id=id)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_job(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id).first()

    if not job or not (current_user.id == job.team_leader or current_user.id == 1):
        abort(404)

    db_sess.delete(job)
    db_sess.commit()

    return redirect('/jobs')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.hashed_password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/jobs")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


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
            surname=form.surname.data,
            name=form.name.data,
            age=int(form.age.data),
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.email.data,
            hashed_password=form.password.data
        )

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


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
