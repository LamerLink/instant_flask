#!"ph_for_vpy_path"
import os
from waitress import serve
from flask import (
    Flask,
    request,
    redirect,
    render_template,
    flash,
    send_file,
    url_for,
    Markup
)
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user
)
from flask_talisman import Talisman
from flask_mobility import Mobility
from functions import (
    Security,
    User,
    Passworder,
    SERVE_DIR,
    UPLOAD_DIR,
    LoginForm,
    ResetForm,
    UpdateForm
)
from blueprints import (
    admin_blueprint,
    download_example_blueprint,
    home_blueprint
)


# The max upload size set in megabytes
MAX_MB_UPLOAD = 500

# The web application itself
app = Flask(__name__)
# For handling mobile devices differently
Mobility(app)
# You can use Talisman to force HTTPS redirect
#Talisman(app, content_security_policy=None)
# Required for encryption
app.config['SECRET_KEY'] = 'ph_for_secret'
# Directory to receive uploaded files to
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
# Form expiry set to every 2 days, adjust this based on security needs
app.config['WTF_CSRF_TIME_LIMIT'] = 172800
# Setting the max file size limit
app.config['MAX_CONTENT_LENGTH'] = MAX_MB_UPLOAD * 1024 * 1024

# All blueprints need to be registered to work as routes
app.register_blueprint(admin_blueprint)
app.register_blueprint(download_example_blueprint)
app.register_blueprint(home_blueprint)

# The site's login session manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    check = Security().get(user_id)
    if check:
        user = User(check[0], check[1])
        return user

# Route to login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = Security().ufetch(form.username.data)
        pw_hash = Passworder().get_stored_pw(form.username.data)
        if not pw_hash:
            flash('Username not recognised or invalid.')
        else:
            verify = Passworder().hash_backward(pw_hash, form.password.data)
            if (login and verify):
                login_user(User(*login))
                next = request.args.get('next')
                return redirect(next or url_for('home.home'))
            else:
                flash('Invalid username or password')
    return render_template('form-login.html', form=form, heading='Login')

# Route to reset password.
# Note this route does not work out-of-the-box. You need
# to update/replace the Emailer class.
@app.route("/reset-pw", methods=['GET', 'POST'])
def reset_pw():
    form = ResetForm()
    if form.validate_on_submit():
        new_password = change_to_random_pw(form.email.data)
        if new_password:
            Emailer().send_email(form.email.data, new_password)
            flash('Email sent with reset instructions.')
        else:
            flash('Invalid email, please contact the Help Desk.')
    return render_template(
        'form-reset-pw.html',
        form=form,
        heading='Reset Password'
    )

# Route to let user update password
@app.route("/update-pw", methods=['GET', 'POST'])
@login_required
def update_pw():

    form = UpdateForm()
    if form.validate_on_submit():
        verify = Passworder().hash_backward(
            Passworder().get_stored_pw(current_user.name),
            form.old_pass.data
        )
        if verify:
            new_hashed_pw = Passworder().hash_forward(form.new_pass.data)
            Passworder().update_db_pw(new_hashed_pw, current_user.name)
            flash(
                Markup(
                    (
                        'Password updated successfully. Click '
                        '<a href="/home">here</a> to continue.'
                    )
                )
            )
        else:
            flash('Something went wrong. Check your credentials.')
    return render_template(
        'form-update-pw.html',
        form=form,
        heading='Update Password'
    )

# Logout current session
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.home'))

# Reroute default route to homepage
@app.route("/")
def index():
    return redirect(url_for('home.home'))

# Use this route to serve files to users as downloads
@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(SERVE_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    # Not for production
    app.run(host='ph_for_ip', debug=True, port=ph_for_port)
    # For testing with security certificate
    #ssl = ('some/path/to/file.crt', r'some/path/to/file.key')
    #app.run(host='ph_for_ip', debug=True, port=ph_for_port, ssl_context=ssl)

    # For production
    #serve(app, host='ph_for_ip', port=ph_for_port)
