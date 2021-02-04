from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from jinja2 import Environment

app = Flask(__name__)
app.config['SECRET_KEY'] = '579283eyhu3e8u3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from FairPrim import routes
