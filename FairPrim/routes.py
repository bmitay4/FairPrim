import math
import secrets
import os
from flask import render_template, url_for, flash, redirect, request
from FairPrim.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ElectionForm
from FairPrim.models import User, Post, Election
from FairPrim import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from FairPrim import segal
from string import ascii_lowercase

def update_values():
    posts_count = Post.query.count()
    election_count = Election.query.count()
    return [posts_count, election_count]


@app.route('/')
@app.route('/home')
def home():
    info = update_values()
    posts = Post.query.all()
    return render_template('home.html', posts=posts, total_info=info)


@app.route("/member/<string:username>", methods=['GET', 'POST'])
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)
    form = ElectionForm()
    info = update_values()

    if form.validate_on_submit():
        selected = request.form.getlist('check')
        if len(selected) != posts.first().voted_allow:
            flash('הצבעה לא תקינה, שימו לב לכמות ההצבעות המותרת', 'danger')
            return render_template('user_posts.html', posts=posts, user=user, form=form, total_info=info)

        if db.session.query(Election).get(form.user_id.data):
            flash('תעודת הזהות כבר קיימת במאגר', 'danger')
            return render_template('user_posts.html', posts=posts, user=user, form=form, total_info=info)
        voted = get_checkbox(selected)
        election = Election(id=form.user_id.data, party=user.party, member_voted=voted, user_id=user.id)
        db.session.add(election)
        db.session.commit()
        flash('ההצבעה נקלטה בהצלחה', 'success')
        return redirect(url_for('home'))

    return render_template('user_posts.html', posts=posts, user=user, form=form, total_info=info)


def get_checkbox(selected):
    ans = "-"
    for check in selected:
        ans = ans + str(int(check) - 1) + "-"
    return ans


@app.route('/voting', methods=['GET', 'POST'])
@login_required
def voting():

    open("FairPrim/static/party.txt", 'w').close()
    open("FairPrim/static/party_o.txt", 'w').close()

    posts = Post.query.filter_by(author=current_user).count()
    info = update_values()
    if posts > 0:
        posts = Post.query.filter_by(author=current_user)
        election = Election.query.filter_by(party=current_user.party)
        arr_info = get_info(posts.first(), election.all())

        if election.count() > 0:
            arr_info.insert(8, to_rem(arr_info, current_user.party, current_user.username))
            arr_info.insert(9, len(arr_info[8]))
            arr_info.insert(10, get_candidate_by_char(arr_info))
            edit_txt(arr_info)
        else:
            flash(' אין מידע להצגה, טרם התקבלו הצבעות בפריימריז', 'danger')
            return redirect(url_for('home'))

        return render_template('voting.html', author=current_user, info=arr_info, election=election, posts=posts,
                               total_info=info, avg=round(arr_info[5] / arr_info[3], 4),
                               max=math.ceil(1 / (arr_info[5] / arr_info[3])))
    else:
        flash('לא יצרת עדיין פריימריז', 'danger')
        return redirect(url_for('home'))


# Returning a map of candidates converted to abc, and their weights (even to 1)
def calculate_algo(post: Post):
    map_project_to_cost = {}
    for index_1, candidate in enumerate(post.members.split(', ')):
        for index_2, c in enumerate(ascii_lowercase):
            if index_1 == index_2:
                map_project_to_cost[c] = 1

    return map_project_to_cost


def to_rem(arr_info, party, username) -> list:
    return segal.run(arr_info[6], arr_info[7], arr_info[5],party, username)


def get_candidate_by_char(info):
    results = []
    for index, candidate in enumerate(info[6]):
        for winner in info[8]:
            if candidate == winner:
                results.append(info[1][index])

    return results


def get_info(post: Post, election: Election):
    arr_info = []
    arr_info.insert(0, len(post.members.split(', ')))
    arr_info.insert(1, post.members.split(', '))
    voting_arr: int = [0] * arr_info[0]
    arr_info.insert(2, voting_arr)

    candidate_dic = calculate_algo(post)

    for voter in election:
        for internal_index, single_vote in enumerate(voter.member_voted):
            if internal_index % 2 != 0:
                for candidate in range(arr_info[0]):
                    if int(single_vote) == candidate:
                        arr_info[2].insert(candidate, arr_info[2][candidate] + 1)
                        arr_info[2].pop(candidate + 1)

    arr_info.insert(3, sum(arr_info[2]))
    voting_by_users = [] * 2 * arr_info[3]
    arr_info.insert(4, voting_by_users)
    if post.polls_predict == "":
        arr_info.insert(5, arr_info[0])
    else:
        arr_info.insert(5, post.polls_predict)
    if post.voted_allow == 1:
        converted_voting_by_users = [0] * arr_info[3]
    else:
        converted_voting_by_users = [0] * int((arr_info[3]/int(post.voted_allow)))
    arr_info.insert(6, candidate_dic)
    arr_info.insert(7, converted_voting_by_users)
    for index, voter in enumerate(election):
        total_vote = ""
        total_converted_vote = ""
        for internal_index, single_vote in enumerate(voter.member_voted):
            if internal_index % 2 != 0:
                for candidate in range(arr_info[0]):
                    if int(single_vote) == candidate:
                        total_converted_vote = total_converted_vote + get_candidate_value(candidate_dic, candidate)
                        total_vote = total_vote + arr_info[1][int(single_vote)] + ", "
        if len(total_vote) > 0:
            arr_info[4].insert(index, [voter.id, total_vote[:-2]])
        if len(total_converted_vote) > 0:
            arr_info[7][index] = total_converted_vote

    return arr_info


def get_candidate_value(candidate_dic: dict, candidate) -> str:
    return str(list(candidate_dic)[candidate])


def edit_txt(info):
    fin = open("FairPrim/static/party.txt", "rt")
    fout = open("FairPrim/static/party_o.txt", "wt")

    for line in fin:
        newline = line
        for index_1, c in enumerate(ascii_lowercase):
            if index_1 < len(info[1]):
                if line.__contains__(c):
                    newline = newline.replace(c, info[1][index_1]+" - ")
        fout.write(newline)

    fin.close()
    fout.close()

@app.route('/algorithm')
def algorithm():
    info = update_values()
    return render_template('algorithm.html', title='Algorithm', total_info=info)


@app.route('/about')
def about():
    info = update_values()
    return render_template('about.html', title='About', total_info=info)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    info = update_values()

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
    return render_template('signup.html', title='Sign Up', form=form, total_info=info)


@app.route('/login', methods=['GET', 'POST'])
def login():
    info = update_values()

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
    return render_template('login.html', title='Login', form=form, total_info=info)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    info = update_values()

    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, date_posted=form.date.data,
                    members=form.members.data, polls_predict=form.polls_predict.data, voted_allow=form.voted_allow.data)
        db.session.add(post)
        db.session.commit()
        flash('מועד הפריימריז נוצר בהצלחה!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, total_info=info)


@app.route('/post/<int:post_id>')
def post(post_id):
    info = update_values()

    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post, total_info=info)


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
    info = update_values()

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
    return render_template('account.html', title='My Account', image_file=image_file, form=form, total_info=info)
