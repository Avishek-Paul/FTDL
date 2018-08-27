from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'password'})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateTask(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], render_kw={'placeholder': 'title'})
    author = StringField('Author', validators=[DataRequired()], render_kw={'placeholder': 'author'})
    content = StringField('Content', validators=[DataRequired()], render_kw={'placeholder': 'content'})
    assignees = StringField('Assignees', validators=[DataRequired()], render_kw={'placeholder': 'assignees'})
    create = SubmitField('Create')