import os
import hashlib
import binascii
import random
from flask_login import UserMixin
from typing import Union
from db import SQL
# If you'd like to raise an exception on login failure, you could use this
#from functions.loc_exceptions import AuthenticationFailureError


# This is an example security class based on Miguel Grinberg's tutorial
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
class Security():
    def __init__(self) -> None:
        sql = SQL()
        self.connection = sql.connection
        self.cursor = sql.cursor

    def ufetch(self, username: str) -> Union[bool, str]:
        query = (
            "select user_id, username, hashed_pw from venv_user"
            " where username = ?"
        )
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchall()
        # Ensure only one of this user id and pw combo exist
        if len(result) != 1:
            return False
        else:
            user_id = result[0]
            return user_id

    def get(self, user_id: str) -> Union[bool, str]:
        query = 'select username, user_id from venv_user where username = ?'
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchall()
        # Ensure only one of this user id and pw combo exist
        if len(result) != 1:
            return False
        else:
            user_id = result[0]
            return user_id

class User(UserMixin):
    def __init__(self, name: str, id: str, active: bool = True) -> None:
        self.name = name
        self.id = id
        self.active = active

    def get(self, id: str) -> None:
        result = Security().get(id)
        if result:
            return result
        else:
            return None

    def is_active(self) -> None:
        # All users are active by default
        pass

    def is_anonymous(self) -> None:
        return False

    def is_authenticated(self) -> None:
        return True

class Passworder():
    def __init__(self) -> None:
        sql = SQL()
        self.connection = sql.connection
        self.cursor = sql.cursor

    def hash_forward(self, password: str) -> bool:
        # Hash the password
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            100000
        )
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def hash_backward(self, stored_password: str,
                      provided_password: str) -> bool:
        # Check a stored hash's accuracy against a pw
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            provided_password.encode('utf-8'),
            salt.encode('ascii'),
            100000
        )
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    def get_stored_pw(self, username_or_email: str) -> Union[bool, str]:
        select_query = ('select hashed_pw from venv_user '
                        'where username = ? or email = ?')
        self.cursor.execute(select_query, (username_or_email, username_or_email))
        try:
            result = self.cursor.fetchall()[0][0]
        except IndexError:
            result = False
        return result

    def update_db_pw(
        self,
        hashed_password: str,
        username_or_email: str
    ) -> bool:
        select_query = (
            'select user_id, username from venv_user'
            ' where username = ? or email = ?'
        )
        self.cursor.execute(select_query, (username_or_email, username_or_email))
        result = self.cursor.fetchall()
        # Ensure only one of this user id and pw combo exist
        if len(result) != 1:
            return False
        else:
            update_query = ('update venv_user set password = ? '
                            'where email = ? or username = ?')
            self.cursor.execute(update_query, (hashed_password,
                                               username_or_email,
                                               username_or_email)
                                )
            self.connection.commit()
            return True

def change_to_random_pw(email: str) -> Union[bool, str]:
    random_password = ''.join(map(str, random.sample(range(10), 8)))
    hashed_password = Passworder().hash_forward(random_password)
    update = Passworder().update_db_pw(hashed_password, email)
    if update:
        return random_password
    else:
        return False

def create_user(
    username: str,
    password: str,
    last_name: str,
    email: str,
    first_name: str = ''
) -> None:
    pwer = Passworder()
    hashed_pw = pwer.hash_forward(password)
    new_user_query = ("""
        INSERT INTO [venv_user]
        ([username],[hashed_pw],[last_name],[first_name],[email])
        VALUES (?, ?, ?, ?, ?)"""
        )
    pwer.cursor.execute(
        new_user_query,
        (
            username,
            hashed_pw,
            last_name,
            first_name,
            email
        )
    )
    pwer.connection.commit()

def delete_user(user_id: str) -> None:
    sql = SQL()
    del_user_query = "DELETE FROM [venv_user] WHERE user_id = ?"
    sql.cursor.execute(del_user_query, (user_id,))
    sql.connection.commit()

def get_all_users() -> list:
    sql = SQL()
    cursor = sql.cursor
    cursor.execute('select user_id, username from venv_user')
    return cursor.fetchall()
