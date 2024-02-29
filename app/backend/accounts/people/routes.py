# app/backend/accounts/people/routes.py

# Import necessary libraries
from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from ...database.models import User, Settings
from .forms import AddUserForm, EditUserForm, EditProfilePictureForm
from .utils import handle_add_new_users, change_password, validate_new_password, save_profile_picture, delete_user


people_bp = Blueprint('people', __name__, url_prefix='/people')


@people_bp.route('/people_list', methods=['GET', 'POST'])
@login_required
def people_list():
    """
    Renders the page showing a list of people.

    Returns:
        render_template: Renders the 'accounts/people_list.html' template.
    """
    if current_user.is_authenticated:
        people_list = User.query.all()
        add_form = AddUserForm()

        # Retrieve house sections and populate the choices
        house_sections = []
        settings = Settings.query.first()
        if settings and settings.house_sections:
            house_sections = [(section, section) for section in settings.house_sections.split(',')]

        return render_template('accounts/people_list.html', people_list=people_list, house_sections=house_sections, form=add_form, hide_footer=True)
    else:
        return redirect(url_for('auth.login'))


@people_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    """
    Handles adding a new user.

    Returns:
        redirect: Redirects to the people list page.
    """
    if current_user.is_authenticated:
        add_form = AddUserForm()

        if request.method == 'POST':
            form_type = request.form.get('form_type')

            if form_type == 'add':
                result = handle_add_new_users(add_form, current_user)

                if result['success']:
                    flash(result['message'], 'success')
                else:
                    flash(result['message'], 'danger')
        return redirect(url_for('accounts.people.people_list', people_list=people_list, form=add_form, hide_footer=True))
    else:
        return redirect(url_for('auth.login'))


@people_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """
    Handles editing a user's information.

    Args:
        user_id (int): The ID of the user to edit.

    Returns:
        render_template: Renders the 'accounts/edit_people.html' template.
        redirect: Redirects to the people list page.
    """
    if current_user.is_authenticated:
        user = User.query.get_or_404(user_id)
        form = EditUserForm(request.form, obj=user)

        # Populate house sections choices
        form.populate_house_sections()

        if request.method == 'POST' and form.validate():
            if form.new_password.data:
                if not validate_new_password(form.new_password.data):
                    flash('New password must be at least 6 characters long.', 'danger')
                    return render_template('accounts/edit_people.html', user=user, form=form, hide_footer=True)
                else:
                    # Change password only if new password is provided
                    change_password(user, form)

            # Check if there are other users in the same house section and house number with a main account
            all_house_accounts = User.query.filter_by(house_section=user.house_section, house_number=user.house_number).all()

            # Check if there is a main account in the same house section and house number
            if any(account.main_account for account in all_house_accounts):
                # If there is a main account, set the current user as not the main account
                user.main_account = False
            else:
                # If there are no main accounts, set the current user as the main account
                user.main_account = True

            # Update user profile
            form.populate_obj(user)
            db.session.commit()

            flash(f'Successfully updated profile for {user.first_name.title()}.', 'success')
            return redirect(url_for('accounts.people.people_list'))

        return render_template('accounts/edit_people.html', user=user, form=form, hide_footer=True)
    else:
        return redirect(url_for('auth.login'))


@people_bp.route('/edit_profile_picture', methods=['GET', 'POST'])
@login_required
def edit_profile_picture_route():
    """
    Handles editing a user's profile picture.

    Returns:
        render_template: Renders the 'accounts/edit_people.html' template.
        redirect: Redirects to the people list page.
    """
    if current_user.is_authenticated:
        form = EditProfilePictureForm()

        if request.method == 'POST' and form.validate():
            if form.profile_image.data:
                if save_profile_picture(form.profile_image.data):
                    flash('Profile picture updated successfully.', 'success')
                    return redirect(url_for('accounts.people.people_list'))
                else:
                    flash('Error updating profile picture.', 'danger')

        return render_template('accounts/edit_people.html', form=form)
    else:
        return redirect(url_for('auth.login'))


@people_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user_route(user_id):
    """
    Handles deleting a user.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        redirect: Redirects to the people list page.
    """
    if current_user.is_authenticated:
        user = User.query.get_or_404(user_id)

        if user == current_user:
            flash('You cannot delete your own account.', 'danger')
            return redirect(url_for('accounts.people.people_list'))

        if delete_user(user):
            flash(f'Successfully deleted the user {user.first_name.title()}.', 'success')
        else:
            flash(f'Error deleting the user {user.first_name.title()}.', 'danger')

        return redirect(url_for('accounts.people.people_list'))
    else:
        return redirect(url_for('auth.login'))

from ..components.download_manager import download_users

@people_bp.route('/download_users', methods=['GET'])
@login_required
def download_users_route():
    return download_users()
