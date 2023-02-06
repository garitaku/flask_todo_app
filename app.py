from datetime import datetime, date
from flask import Flask, render_template, request, redirect
from flask_login import UserMixin, LoginManager, login_user,login_required,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy

import os
from werkzeug.security import generate_password_hash, check_password_hash

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = os.urandom(24)
# initialize the app with the extension
db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),
        nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12))
    posts = db.relationship('Post')



with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/<string:username>', methods=['GET', 'POST'])
@login_required
def index(username):
    if request.method == 'GET':
        # タスク期限が近い順に投稿を全部持ってくる
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.due).all()
        return render_template('index.html', posts=posts, today=date.today(),user=current_user)
    else:
        user_id = current_user.id
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        new_post = Post(title=title, detail=detail, due=due,user_id=user_id )
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect('/'+ username)
        except:
            return "フォームの送信中に問題が発生しました"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        new_user = User(username=username, password=generate_password_hash(password,method='sha256'))

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        except:
            return "フォームの送信中に問題が発生しました"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        user=User.query.filter_by(username=username).first()
        if check_password_hash(user.password,password):
            login_user(user)
            return redirect('/'+ user.username)

@app.route('/logout')
@login_required #デコレータ(ログアウトするにはログインされているのが前提)
def logout():
    logout_user()
    return redirect('/login')



@app.route('/<string:username>/create')
@login_required
def create(username):
    return render_template('create.html',username=username)


@app.route('/<string:username>/detail/<int:id>')
@login_required
def read(username,id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post,username=username)


@app.route('/<string:username>/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id,username):
    post = Post.query.get(id)
    if request.method == 'GET':
        # updateのページ
        return render_template('update.html', post=post,user=current_user)
    else:
        # dbに反映
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')
        db.session.commit()
        # トップページに
        return redirect('/'+username)


@app.route('/<string:username>/delete/<int:id>')
@login_required
def delete(id,username):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/'+username)


if __name__ == '__main__':
    app.run(debug=True)
