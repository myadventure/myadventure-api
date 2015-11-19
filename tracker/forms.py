from flask.ext.wtf import Form
from wtforms.fields import TextField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(Form):
    email = TextField('email', validators=[DataRequired()])
    password = TextField('password', validators=[DataRequired()])
    remember = BooleanField('remember')
