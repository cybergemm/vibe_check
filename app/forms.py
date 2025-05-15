"""
Defines form classes for the Vibe Check web application using Flask-WTF and WTForms,
including forms for login, signup, privacy settings, password change, and account deletion.
"""
# Import FlaskForm from flask_wtf or define a dummy base class if unavailable.
try:
    from flask_wtf import FlaskForm
except ImportError:
    class FlaskForm(object):
        pass

# Import field types and validators used to build the forms.
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

# Form for logging in with username, password, and a "remember me" option.
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

# Form for registering a new user with validation for matching and secure passwords.
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    remember = BooleanField('Remember Me')

# Form for selecting a user’s privacy setting from predefined options.
class PrivacyForm(FlaskForm):
    privacy_setting = SelectField('Privacy', choices=[
        ('public', 'Everyone'),
        ('friends', 'Friends Only'),
        ('private', 'Private')
    ], validators=[DataRequired()])

# Form for changing a user's password with confirmation and length validation.
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])

# Empty form for account deletion, relying on CSRF token for protection.
class DeleteAccountForm(FlaskForm):
    pass  # No fields needed, just CSRF