from datetime import datetime,date
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)


try:
    with app.app_context():
        db.create_all()
except:
    print('既にデータベースが作成されています')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        #タスク期限が近い順に投稿を全部持ってくる
        posts = Post.query.order_by(Post.due).all()
        return render_template('index.html', posts=posts,today=date.today())
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        new_post = Post(title=title, detail=detail, due=due)
        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
        except:
            return "フォームの送信中に問題が発生しました"


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/detail/<int:id>')
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        # updateのページ
        return render_template('update.html', post=post)
    else:
        # dbに反映
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'),'%Y-%m-%d')
        db.session.commit()
        # トップページに
        return redirect('/')



@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
