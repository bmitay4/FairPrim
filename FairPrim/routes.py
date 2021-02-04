import secrets
import os
from flask import render_template, url_for, flash, redirect, request, jsonify, json
from FairPrim.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ElectionForm
from FairPrim.models import User, Post, Election
from FairPrim import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/member/<string:username>", methods=['GET', 'POST'])
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)
    form = ElectionForm()

    if form.validate_on_submit():
        print(form.user_id.data)
        print(form.member.data)
        election = Election(id=form.user_id.data, party=user.party, member_voted=str(int(form.member.data)-1), user_id=user.id)

        db.session.add(election)
        db.session.commit()
        flash('ההצבעה נקלטה בהצלחה', 'success')
        return redirect(url_for('home'))

    return render_template('user_posts.html', posts=posts, user=user, form=form)


@app.route('/voting', methods=['GET', 'POST'])
@login_required
def voting():
    posts = Post.query.filter_by(author=current_user)
    election = Election.query.filter_by(party=current_user.party)
    election_count = Election.query.filter_by(party=current_user.party).count()

    return render_template('voting.html', author=current_user, election=election, posts=posts, count=election_count)


@app.route('/algorithm')
def algorithm():
    return render_template('algorithm.html', title='Algorithm')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, party=form.party.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data}, חשבונך נוצר בהצלחה', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful, please check your credentials ans try again', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, date_posted=form.date.data,
                    members=form.members.data)
        db.session.add(post)
        db.session.commit()
        flash('מועד הפריימריז נוצר בהצלחה!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


def save_picture(form_picture):
    random_hacks = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hacks + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


def save_picture_party(form_picture):
    random_hacks = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hacks + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        if form.party_picture.data:
            party_picture = save_picture_party(form.party_picture.data)
            current_user.party_image_file = party_picture

        current_user.username = current_user.username
        current_user.email = form.email.data
        current_user.party = current_user.party
        db.session.commit()
        flash('הפרטים עודכנו בהצלחה', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.party.data = current_user.party
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='My Account', image_file=image_file, form=form)
