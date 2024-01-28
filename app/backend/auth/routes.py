# app/backend/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app.backend.models.user import User, db
from app.backend.accounts import accounts_bp
from app.backend.auth.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mobile_number=form.mobile_number.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Login successful, Welcome back {user.first_name.title()}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('accounts.dashboard.dashboard'))
        else:
            flash('Invalid mobile number or password. Please try again.', 'danger')
    return render_template('auth/login.html', form=form, hide_navbar=True, hide_sidebar=True, hide_footer=True)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            mobile_number=form.mobile_number.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, hide_navbar=True, hide_sidebar=True, hide_footer=True)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('landing.landing'))

