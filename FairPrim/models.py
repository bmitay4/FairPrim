from FairPrim import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    party = db.Column(db.String(20), nullable=False)
    # party_img = db.Column(db.String(20), nullable=False, default='party.png')
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    party_image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    post = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}',{self.party}, '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Text, nullable=False)
    members = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    polls_predict = db.Column(db.Integer, nullable=True)
    voted_allow = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.content}', '{self.members}', '{self.polls_predict}', '{self.voted_allow}')"


class Election(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    party = db.Column(db.String(20), nullable=False)
    member_voted = db.Column(db.String(8), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Election('{self.id}', '{self.party}', '{self.member_voted}', '{self.user_id}')"
