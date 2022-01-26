# InstantFlask

A simple project that creates a template Flask web application in a virtual environment.

## Requirements and Supported Environments
Python 3.7+ and Windows or Linux (tested on Ubuntu 21.04). MacOS is currently not supported as I don't have a MacOS machine to readily test on.

The following Python modules are required, and automatically installed in the virtual environment during setup.
* waitress
* flask
* flask-login
* flask-talisman
* flask-mobility
* flask-wtf
* flask-sqlalchemy
* email-validator
* openpyxl
* python-dateutil

## Setup
To use this script, first ensure you have the requisite Python version installed.

Download the source or clone the repo, then run the `build.py` script. It will look for the `environment` folder and prompt you for various inputs.

### Create the Database
After running the build script, you need to set up a user database. Ideally this won't be on the same server as the application, certainly not in a production environment! By default, the test application is configured to use [SQLite3](https://www.sqlite.org/). You can always go through and change this, of course.

See the Database section in the Site Walkthrough below for the default expected database schema.

## Coming Soon
I'm hoping to add  a couple additions eventually, feel free to help me.
* An example page with numerous form fields.
* GUI setup

## Site Walkthrough

### Database
The default database contains a single table and is only used for user sign-ins.

By default, the application uses Python's interface for sqlite3. You're encouraged to use [`pyodbc`](https://pypi.org/project/pyodbc/) to connect to a production database insetad, but this will require additional work. **It is not recommended to keep a database or user login information, albeit hashed, on the same server as the application.**

```SQL
CREATE TABLE [venv_user] (
[user_id] integer PRIMARY KEY AUTOINCREMENT,
[username] varchar(50) COLLATE NOCASE NOT NULL,
[hashed_pw] text COLLATE NOCASE NOT NULL,
[last_name] varchar(50) COLLATE NOCASE NOT NULL,
[first_name] varchar(50) COLLATE NOCASE NULL,
[email] varchar(50) COLLATE NOCASE NOT NULL)
```

### Blueprints
Flask Blueprints are used to keep the site more organised and maintainable. I strongly recommend you read [the documentation on blueprints](https://flask.palletsprojects.com/en/2.0.x/blueprints/).

Blueprints are sort of like mini-Flask applications that link into the main app. They provide a *blueprint* for the application, keeping the main `app.py` file from becoming overencumbered with a lot of endpoints. This is especially handy when endpoints become more complex.

Each blueprint is declared in a separate file within the `blueprints` folder, imported into the main `app.py` file, and then registered via `app.register_blueprint(some_blueprint)`.

### Templating
`Flask` uses the [`Jinja2` templating engine](https://pypi.org/project/Jinja2/) for webpage templating. This is a handy, verbose tool that allows html documents to be passed Python parameters, rendering webpages dynamically. This keeps the html development to a minimum, and also promotes an object-oriented approach to web development.

Each template is saved to the `templates` folder. In an endpoint, the `flask.render_template` method is used to pull the template and pass the parameters. Flask automatically is configurd to look for templates in a folder named `templates` in the same directory as the `app.py` file.

I recommend you review either the [`Jinja2` documentation](https://jinja.palletsprojects.com/en/3.0.x/) or [`Flask` templating documentation](https://flask.palletsprojects.com/en/2.0.x/tutorial/templates/) to familiarise yourself with the templating engine's syntax. In soem cases, the syntax mirrors Python greatly, but others do not. For example, checking if the length of a list is greater than 5 in `Jinja2` is `{% if a_list|length > 5 %}` as opposed to Python's `if len(a_list) > 5:`.

### Functions
The `functions` folder houses some helpful references/functions used throughout the site. Some may be useless to you, but the two you'll want to familiarise yourself with are `forms.py` and `security.py`. The former holds the forms used throughout the templates, and the latter holds the functions used to authenticate, create, and delete users.

An explanation of each file and it's purpose follows.

<hr>

#### emailer.py

##### `send_email`
This function does not work out-of-the-box. It uses the built-in Python email capabilities and can be adjusted for your organization to send emails. I reference it in the password reset endpoint to send temporary passwords to users' email accounts if they forget passwords.

You may also find some other packages such as [`exchangelib`](https://pypi.org/project/exchangelib/) or [`yagmail`](https://pypi.org/project/yagmail/) useful, to name a few.

<hr>

#### exporter.py

##### `ExportFile`
This class is instantiated to write a `sqlite3` or `pyodbc` result set (acquired using `fetchall`) to csv or xlsx format. You may find a better/easier way to do this, such as using the [`pandas`](https://pypi.org/project/pandas/) module.

<hr>

#### forms.py
I use [`flask_wtf`](https://pypi.org/project/Flask-WTF/) to easily handle webforms. This is not strictly required, but it makes it simple to gather and parse data. Each form nherits the base `FlaskForm` object. I recommend you review the [`Flask-WTF` documentation](https://flask-wtf.readthedocs.io/en/0.15.x/) for more information.

Some fields use `wtforms.validators` to validate the data being receiving is the correct type, too.

##### `LoginForm`
Receives input to verify user login. Password is obfuscated. On successful login, a user session is created via the `flask_login.LoginManager`.

##### `ResetForm`
Receives input for a user to send a temporary password to their email to change their password. *Note the email function does not work out-of-the-box.*

##### `UpdateForm`
Receives input for a user to change the password.

##### `CreateUserForm`
Receives input for user creation.

This form shares a page with the `DeleteUserForm` and so each are identified via an `id="name"` attribute in the `admin.html` template.

##### `DeleteUserForm`
Receives input for deletion of user(s).

Something unique to note about this form beside what was noted in the shared-page `CreateUserForm` above is that it has only a submit button. This is because the checkboxes used to select multiple users are parsed via the `flask.request.form` parameter when the form is submitted. Check the `admin_bp.py` file to see this logic.

<hr>

#### loc_exceptions.py
This file holds any local exceptions you may wish to create and import throughout the project.

##### `AuthenticationFailureError`
An example exception that is not used in the project. you could import this into `security.py` if you wanted to raise an exception when login fails. Then you'd catch it in the endpoint and handle from there.

<hr>

#### misc.py
A group of helper functions. You can remove these but be sure to replace the references throughout the project, particularly the constants.
##### Constants
`PARENT_DIR`, `SERVE_DIR`, and `UPLOAD_DIR`, are local paths that the application references. The first is the directory the application runs from, the second is the directory files can be served from, and the third is the directory that files uploaded to the site will be saved to.

##### `get_time`
This function returns the current datetime as a string.

##### `ensure_unique`
This function ensures a provided file path doesn't exist, and adjusts the provided file to append the current datetime so it does.

<hr>

#### security.py
This file contains classes and functions used in conjunction with the `flask_login.LoginManager` to verify user credentials and update users.

Many of these classes and functions are based directly off of [Miguel Grinberg's tutorial on flask-login](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins).

##### `Security`
Initialises with a `db.SQL` object that returns a `sqlite3` connection.

###### Attributes
* `connection` - the `SQL().connection` attribute passed through. Used to commit updates, inserts, and deletes.
* `cursor` - the `SQL().cursor` method passed through. It is used to run queries.

###### `ufetch`
Used to return a user_id based on email or username.

###### `get`
Verifies that a provided user_id exists and is unique to only one username.

##### `User`
This class inherits from the `flask_login.UserMixin` class.

###### Attributes
* `name` - Username supplied during initialisation.
* `id` - User ID supplied during initialisation.
* `active` - Bool, defaults to `True`.

###### `get`
Invokes `Security().get()` to verify a user exists and is distinct.

###### `is_active`
Unused in this example, all users are active by default. Can be used to verify a user is not disabled.

###### `is_anonymous`
Needs updating. All valid users are not anonymous.

###### `is_authenticated`
Needs updating. All valid users are authenticated if password is correct.

##### `Passworder`
This class handles the setting, hashing, and verification of passwords.

###### Attributes
* `connection` - the `SQL().connection` attribute passed through. Used to commit updates, inserts, and deletes.
* `cursor` - the `SQL().cursor` method passed through. It is used to run queries.

###### `hash_forward`
A function that uses the `hashlib` library to hash passwords. This is used to prevent plaintext passwords from being stored in the database.

###### `hash_backward`
A function that verifies a password provided matches the hashed password stored in the database.

###### `get_stored_pw`
Returns the `hashed_pw` for a given username or email from the database.

###### `update_db_pw`
A function to change the stored database `hashed_pw` for a given user.

<hr>

##### Other `security.py` helpers

###### `change_to_random_pw`
A function that changes a given user's password to a random value in the database and provides the password as plaintext to be used in a secure email.

**Note that this function does not require the original password.** It should be used for reset purposes where the recipient must login to an email account connected to the account to retrieve the temporary password.

###### `create_user`
A function to create a new user. Requires the following inputs:
* username
* password
* last_name
* email
* first_name

###### `delete_user`
A function to delete a give user based on their `user_id`.

Does not accept multiple IDs concurrently.

###### `get_all_users`
Retrieves all users and their IDs.

## Credits
Much of the code from this project was adapted from solutions found on StackOverflow over the years. I wish I could credit everyone, my thanks to all the developers out there.

* [Miguel Grinberg's amazing Flask guides](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).
* CSS slightly modified from [Dave Gamache's Skeleton V2.0.4](http://getskeleton.com/).
