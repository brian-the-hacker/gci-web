from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms import SubmitField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.validators import InputRequired
from wtforms import StringField, TextAreaField, SubmitField, FileField, BooleanField
from wtforms.validators import DataRequired, Optional
from wtforms import StringField, TextAreaField, BooleanField, FileField, DateField
from wtforms import FileField
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField



class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[('general', 'General'), ('event', 'Event')])
    event_date = DateField('Event Date', format='%Y-%m-%d')
    image_url = FileField('Upload Image')  # New field for file upload
    
class CreatePasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

# Registration form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')



class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
    
class UploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Images', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Create Post')