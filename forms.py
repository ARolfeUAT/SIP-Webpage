from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields.simple import FileField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo


class RegisterForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    """Form for creating blog posts."""
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content (Markdown)', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    """Form for adding comments."""
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')
