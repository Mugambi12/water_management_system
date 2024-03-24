# File: app/backend/auth/password_reset_utils.py

# Import necessary modules
from flask import flash, redirect, url_for, render_template, current_app, url_for, jsonify
from werkzeug.security import generate_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app import mail, db
from app.utils import generate_random_string
from ..database.models import User, PasswordResetToken, MailSettings


def generate_token(email):
    with current_app.app_context():
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        salt = current_app.config.get('SECURITY_PASSWORD_SALT', generate_random_string())
        return serializer.dumps(email, salt=salt)

#async def send_async_email(msg):
#    try:
#        mail.send(msg)
#        return True
#    except Exception as e:
#        print(f"Failed to send email: {e}")
#        return False

def send_async_email(msg):
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_password_reset_email(email, token):
    reset_link = url_for('auth.reset_password', token=token, _external=True)

    #mail_settings = MailSettings.query.first()
    #sender_email = mail_settings.company_email if mail_settings else current_app.config['MAIL_USERNAME']
    sender_email = current_app.config['MAIL_USERNAME']

    msg = Message('Password Reset Request', recipients=[email], sender=sender_email)

    email_body = (
        "Dear user,\n\n"
        "We received a request to reset your password. If you didn't make this request, you can ignore this email.\n\n"
        "To reset your password, please click on the following link:\n"
        f"{reset_link}\n\n"
        "If you're unable to click on the link, you can copy and paste it into your browser's address bar.\n\n"
        "This link will expire after a certain period of time for security reasons.\n\n"
        "If you have any questions or need further assistance, please don't hesitate to contact us.\n\n"
        "Best regards,\n"
        "ApoGen Solutions Team"
    )

    msg.body = email_body

    return send_async_email(msg)

def _reset_password_request(form):
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            token = generate_token(form.email.data)
            reset_token = PasswordResetToken(email=form.email.data, token=token)
            db.session.add(reset_token)
            db.session.commit()
            if send_password_reset_email(form.email.data, token):
                return jsonify({"message": "An email with instructions to reset your password has been sent.", "type": "success"})
            else:
                return jsonify({"message": "Failed to send password reset email. Please try again later.", "type": "danger"})
        else:
            return jsonify({"message": "Email not found in our users.", "type": "warning"})

    return render_template('auth/reset_password_request.html', form=form, hide_navbar=True, hide_sidebar=True, hide_footer=True)

def _reset_password(token, form, reset_token):
    if form.validate_on_submit():
        # Find the user by email
        user = User.query.filter_by(email=reset_token.email).first()

        if user:
            # Update user password
            user.password_hash = generate_password_hash(form.password.data)
            # Delete the reset token
            db.session.delete(reset_token)
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid user or expired token.', 'danger')
            return redirect(url_for('auth.reset_password_request'))

    # Pass the token to the template
    form.token.data = token
    return render_template('auth/reset_password.html', form=form, token=token, hide_navbar=True, hide_sidebar=True, hide_footer=True)
