from flask import (
    Blueprint,
    Markup,
    render_template,
    flash,
    request,
    redirect,
    url_for
)
from flask_login import login_required, current_user
from dateutil.parser import parse
from functions import (
    CreateUserForm,
    DeleteUserForm,
    get_all_users,
    create_user,
    delete_user
)


# Define the Blueprint object
admin_blueprint = Blueprint('admin', 'app')

# Set the Blueprint's route and methods
@admin_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    heading = 'Administration'
    description = 'Use the below forms to administrate users.'
    user_details = f'{current_user.name} ({current_user.id})'
    create_form = CreateUserForm()
    delete_form = DeleteUserForm()
    users = get_all_users()
    # Since there are multiple forms on one page, we need to check both
    # validate_on_submit and that the forms submit button was clicked.
    if request.method == 'POST':
        # Form control for creating users
        if create_form.validate_on_submit() and create_form.submit.data:
            create_user(
                create_form.username.data,
                create_form.password.data,
                create_form.last_name.data,
                create_form.email.data,
                create_form.first_name.data
            )
            success = True
            success_message = f'User {create_form.username.data} created!'
        # Form control for deleting
        elif delete_form.validate_on_submit() and delete_form.submit.data:
            target_users = []
            user_ids = [str(i[0]) for i in users]
            for i in user_ids:
                checked = request.form.get(i)
                if checked:
                    target_users.append(i)
            if len(target_users) == 0:
                success = False
                flash('Choose users to delete.')
            else:
                for user_id in target_users:
                    delete_user(user_id)
                success = True
                success_message = 'Users deleted!'
        # Errors
        else:
            print('Error found in a form.')
            print(create_form.errors)
            print(delete_form.errors)
            success = False
        if success:
            # Clear fields
            fields_to_clear = [
                create_form.username,
                create_form.password,
                create_form.last_name,
                create_form.email,
                create_form.first_name
            ]
            for i in fields_to_clear:
                i.data = ''
            flash(success_message)
    return render_template('admin.html', heading=heading,
                           description=description, users=users,
                           user_details=user_details,
                           forms=[create_form, delete_form])
