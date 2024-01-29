# app/backend/accounts/people/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import EqualTo, DataRequired, Email, Length, Optional
from flask_wtf.file import FileField, FileAllowed


class AddUserForm(FlaskForm):
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    house_section = StringField('House Section', validators=[DataRequired(), Length(max=20)])
    house_number = StringField('House Number', validators=[DataRequired(), Length(max=10)])
    is_active = BooleanField('Active')
    is_admin = BooleanField('Admin')

    submit = SubmitField('Add User')

class EditUserForm(FlaskForm):
    # Personal Information
    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[Optional()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired()])

    # Contact Information
    email = StringField('Email', validators=[Email(), Optional()])

    # Address Information
    house_section = StringField('House Section', validators=[Optional()])
    house_number = StringField('House Number', validators=[Optional()])

    # Profile Image URL
    profile_image = StringField('Profile Image URL', validators=[Optional()])

    # User Status
    is_active = BooleanField('Active', validators=[Optional()])
    is_admin = BooleanField('Admin', validators=[Optional()])

    # Password fields for admin users
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[EqualTo('confirm_new_password', message='Passwords must match'), Optional()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[Optional()])

class EditProfilePictureForm(FlaskForm):
    profile_image = FileField('Profile Image', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'])])
