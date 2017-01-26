"""
forms.py

App forms.
"""

from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    """Login form."""
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    password = PasswordField('Your Password', validators=[DataRequired()])
