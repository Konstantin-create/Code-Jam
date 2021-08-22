# Iports
from datetime import datetime
from werkzeug.urls import url_parse
from flask_login import UserMixin

from config import Config
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, url_for, request, redirect, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, current_user, login_user, login_required
from flask_login import logout_user

from functions import *

# Initializations
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)


# Data base
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    short_discription = db.Column(db.String(300), nullable=False)
    full_discription = db.Column(db.String(100), nullable=True)
    project_type = db.Column(db.String(10), nullable=False)
    file_name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary, nullable=False)
    create_by_id = db.Column(db.Integer)
    create_by_username = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    icon_img = db.Column(db.LargeBinary, unique=True)
    user_description = db.Column(db.Text(300))
    donate_link = db.Column(db.String(300))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Like(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    usrs = db.Column(db.String)

    def __repr__(self):
        return '<Like {}>'.format(self.post_id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Get liked
def liked(post_id, user_id):
    post_like = Like.query.filter_by(post_id=post_id).filter_by(usrs=user_id).first()
    if post_like is not None:
        return True
    return False


# Set like
def set_like(action, post_id, user_id):
    if action == "set":
        post = Like(post_id=post_id, usrs=user_id)
        print(1)
        try:
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            return f'error [{e}]'
    elif action == "offset":
        post = Like.query.filter_by(post_id=post_id, usrs=user_id).first()
        if post is not None:
            db.session.delete(post)
            db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
    custom_img = False
    if current_user.icon_img is not None:
        custom_img = True
    return render_template('index.html', short_name=short_name, custom_img=custom_img, icon_data=current_user.icon_img)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/add-user', methods=['POST'])
def add_user():
    user_name = str(request.form.get('user-name'))
    password = str(request.form.get('user-password'))
    password2 = str(request.form.get('user-repeat-password'))
    user = User.query.filter_by(username=user_name).first()

    if user:
        return render_template('login.html', user_error=True)
    elif user_name.strip() == "":
        return render_template("login.html", user_error=True)
    else:
        if password == password2:
            users = User(username=user_name)
            users.set_password(password)
            try:
                db.session.add(users)
                db.session.commit()
                login_user(users, remember=True)
                return redirect(url_for('main'))
            except Exception as e:
                return f"An error occurred when adding a file. Try again [{e}]"
        return render_template('login.html', password_error=True)


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect('/')
        user_name = request.form.get('user-name')
        password = request.form.get('user-password')
        user = User.query.filter_by(username=user_name).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect('/')
        return render_template('authorization.html', password_error=True)
    return render_template('authorization.html')


@app.route('/posts')
@login_required
def posts():
    return render_template('all-posts.html')


@app.route('/posts/python/<page_id>')
@login_required
def posts_python(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='python').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='Python', img='img/groups/python.png',
                           description=
                           "Here you will find interesting projects, useful scripts in the Python programming language.",
                           posts_type='python', page_id=page_id, all_posts=all_posts_btn, liked=liked,
                           set_like=lambda action, post_id, user_id: set_like(action, post_id, user_id))


@app.route('/posts/c++/<page_id>')
@login_required
def posts_c1(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='c++').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='C++', img='img/groups/c++.png',
                           description=
                           "Here you will find interesting projects, useful scripts in the C++ programming language.",
                           posts_type='c++', page_id=page_id, all_posts=all_posts_btn)


@app.route('/posts/CSharp/<page_id>')
@login_required
def posts_c2(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='c#').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='C#', img='img/groups/c#.png',
                           description=
                           "Here you will find interesting projects, useful scripts in the C# programming language.",
                           posts_type='CSharp', page_id=page_id, len=len, all_posts=all_posts_btn)


@app.route('/posts/html/<page_id>')
@login_required
def posts_html(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='html').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='Html&Css', img='img/groups/html.png',
                           description=
                           "Here you will find unusual websites, interesting ready-made elements, \
                           and incredible combinations of HTML & CSS",
                           posts_type='html', page_id=page_id, len=len, all_posts=all_posts_btn)


@app.route('/posts/java/<page_id>')
@login_required
def posts_java(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='java').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='Java', img='img/groups/java.png',
                           description=
                           "Here you will find interesting projects and apps, useful scripts in the Java programming language.",
                           posts_type='java', page_id=page_id, len=len, all_posts=all_posts_btn)


@app.route('/posts/photoshop/<page_id>')
@login_required
def posts_photoshop(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='photoshop').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='Adobe Photoshop', img='img/groups/photoshop.png',
                           description="Here you will find the most unusual projects performed in Adobe Photoshop Editor",
                           posts_type='photoshop', page_id=page_id, len=len, all_posts=all_posts_btn)


@app.route('/posts/illustrator/<page_id>')
@login_required
def posts_illustrator(page_id):
    page_id = int(page_id)
    posts = []
    posts_data = Posts.query.filter_by(project_type='illustrator').order_by(Posts.date.desc()).all()
    all_posts_btn = False
    for i in range(0, page_id * 12):
        try:
            posts.append(posts_data[i])
        except:
            pass
    if len(posts_data) > 12:
        all_posts_btn = True
    return render_template('posts.html', posts=posts, group='Adobe Illustrator', img='img/groups/illustrator.png',
                           description="Here you will find the most unusual projects performed in \
                                   Adobe Illustrator editor",
                           posts_type='illustrator', page_id=page_id, len=len, all_posts=all_posts_btn)


@app.route('/share')
@login_required
def share():
    return render_template("share-project.html")


@app.route('/upload', methods=['POST'])
def upload():
    title = request.form.get('project-title')
    short_description = request.form.get('short-description-text')
    project_type = request.form.get('select-item')
    files = request.files['file-input']
    create_by_id = current_user.id
    create_by_username = current_user.username
    if validate_db_posts(title, short_description, files):
        return 'All fields must be filed'
    such_post = Posts.query.filter_by(title=title).first()
    if such_post is not None:
        return 'Post with such title is already exists'
    if files.filename == '':
        return 'Please upload file'
    posts = Posts(title=title, short_discription=short_description,
                  project_type=project_type, full_discription="", file_name=files.filename, data=files.read(),
                  create_by_id=create_by_id, create_by_username=create_by_username)
    like = Like(posts.id)

    try:
        db.session.add(posts)
        db.session.add(like)
        db.session.commit()
        return redirect(f'/posts/{project_type}/1')
    except Exception as e:
        return f"An error occurred when adding a file. Try again [{e}]"


@app.route('/download/<file_id>')
@login_required
def download(file_id):
    file_data = Posts.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)


@app.route('/profile/<id>')
@login_required
def profile(id):
    user = User.query.filter_by(id=id).first()
    logo_path = url_for('static', filename='img/user-logo.png')
    description = user.user_description
    if description == None or description == "":
        description = "This user has no description 😕"
    posts = Posts.query.filter_by(create_by_id=id).order_by(Posts.date.desc()).all()
    if len(posts) >= 5:
        return render_template('profile.html', user=user, description=description, posts=posts[:6],
                               more_projects=True, profile_logo_path=logo_path)
    else:
        return render_template('profile.html', user=user, description=description, posts=posts, more_projects=False,
                               profile_logo_path=logo_path)


@app.route('/profile/<int:id>/delete')
@login_required
def delete_profile(id):
    logout_user()
    user = User.query.get_or_404(id)

    try:
        db.session.delete(user)
        db.session.commit()
        return redirect('/')
    except:
        return 'When you delete the user an error occurred'


@app.route('/edit-profile/<id>')
@login_required
def edit_profile(id):
    if str(id) == str(current_user.id):
        return render_template('edit-profile.html')
    else:
        return 'You do not have access to this page.'


@app.route('/set-profile-info', methods=['GET', 'POST'])
@login_required
def set_profile_info():
    if request.method == 'POST':
        user = current_user
        description = str(request.form.get('profile-description'))
        donate_link = str(request.form.get('profile-donate'))
        img = request.files.get('img-input')
        print(img)
        if description is not None:
            description = description.strip()
        if donate_link is not None:
            donate_link = description.strip()

        user.user_description = description
        user.donate_link = donate_link
        #user.icon_img = img.read()


    try:
        db.session.commit()
        return redirect(f'/profile/{current_user.id}')
    except Exception as e:
        return f"An error occurred when adding a file. Try again [{e}]"


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=False)
