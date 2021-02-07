from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from FairPrim.models import User


class RegistrationForm(FlaskForm):
    username = StringField('שם פרטי ושם משפחה', validators=[DataRequired(), Length(min=2, max=20)])
    party = StringField('מפלגה', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('כתובת דוא"ל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמא', validators=[DataRequired()])
    confirm_password = PasswordField('אימות סיסמא', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('הירשם')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('משתמש זה כבר רשום למערכת')

    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError('כבר קיים משתמש עם כתובת הדוא"ל שהזנת במערכת')


class LoginForm(FlaskForm):
    email = StringField('כתובת דוא"ל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמא', validators=[DataRequired()])
    remember = BooleanField('זכור אותי')
    submit = SubmitField('התחבר')


class UpdateAccountForm(FlaskForm):
    username = StringField('שם פרטי ושם משפחה')
    party = StringField('מפלגה')
    email = StringField('כתובת דוא"ל', validators=[DataRequired(), Email()])
    picture = FileField('עדכן תמונתך', validators=[FileAllowed(['jpg', 'png'])])
    party_picture = FileField('עדכן תמונת המפלגה', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('עדכן פרטים')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('משתמש זה כבר רשום למערכת')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(username=email.data).first()
            if user:
                raise ValidationError('כבר קיים משתמש עם כתובת הדוא"ל שהזנת במערכת')


class ElectionForm(FlaskForm):
    user_id = IntegerField('תעודת זהות', validators=[DataRequired()])
    submit = SubmitField('הצבע')


class PostForm(FlaskForm):
    title = StringField('כותרת', validators=[DataRequired()])
    date = DateField('מועד הפריימריז המתוכנן', format='%Y-%m-%d')
    content = TextAreaField('תיאור כללי', validators=[DataRequired()])
    polls_predict = IntegerField('כמות מנדטים צפויה עפ"י הסקרים האחרונים (ניתן להשאיר ריק באם לא קיים שיערוך)')
    members = TextAreaField('רשימת המועמדים', validators=[DataRequired()])
    voted_allow = IntegerField('כמות הצבעות מותרת (ברירת מחדל 1)', validators=[DataRequired()])
    submit = SubmitField('שלח')

