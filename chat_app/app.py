import db_interface as db
from utils import hash_pw
from exceptions import *

from flask import make_response
from connexion.exceptions import OAuthProblem


def session_auth(token, required_scopes):
    try:
        username = db.get_user_from_sid(token)
    except (DBConnectionError, DBInternalError):
        raise OAuthProblem("Internal Server Error: Authorization not available")
    
    if not username:
        username = None
    
    return {'sub': username}


def register_account(body):
    username = body.get("username")
    password = body.get("password")
    # create user
    try:
        if db.user_exists(username):
            return f"Username {username} already in use.", 409
        if not db.create_user(username, hash_pw(password)):
            return f"Username {username} already in use.", 409
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500
    # create sid
    try:
        sid = db.create_session(username)
    except (DBConnectionError, DBInternalError) as e:
        return f"User Account {username} succesfully created. Session ID could not be created.", 201
    # create response object
    res = make_response(f"User Account {username} succesfully created.", 201)
    res.set_cookie("SESSIONID", sid)
    return res

def delete_account(user, body):
    if user == None:
        return "You are currently not logged in.", 403
    # checking the password and deleting the user
    try:
        if db.password_correct(user, hash_pw(body)):
            db.delete_user(user)
            db.delete_session(user)
            res = make_response(f"User Account {user} succesfully deleted.", 200)
            res.set_cookie("SESSIONID", "")
            return res
        else:
            return "The provided password is incorrect.", 403
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500

def post_login(body):
    username = body.get("username")
    password = body.get("password")
    # check username and password
    try:
        if not db.user_exists(username):
            return f"User {username} not found.", 404
        if not db.password_correct(username, hash_pw(password)):
            return "The provided password is incorrect.", 403
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500
    # create sid
    try:
        sid = db.create_session(username)
    except (DBConnectionError, DBInternalError) as e:
        return "Session ID could not be created.", 500
    # create response object
    res = make_response(f"Succesfully logged in to account: {username}", 200)
    res.set_cookie("SESSIONID", sid)
    return res

def get_username(user):
    if user == None:
        return "You are currently not logged in.", 404
    else:
        return user, 200

def logout(user):
    if user == None:
        return "Logged out.", 200
    try:
        db.delete_session(user)
        res = make_response("Logged out.", 200)
        res.set_cookie("SESSIONID", "")
        return res
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500


def send_message(user, receiver, body):
    if user == None:
        return "You are currently not logged in.", 403
    # check if the receiver exists and send the message
    try:
        if not db.user_exists(receiver):
            return f"Receiver {receiver} does not exists.", 404
        if not db.send_message(body, user, receiver):
            return f"Receiver {receiver} does not exists.", 404
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500
    except InternalServerError as e:
        return f"Internal Server Error: {e}", 500
    return "Message sent.", 200

def get_messages_info(user):
    if user == None:
        return "You are currently not logged in.", 403
    # get messages list
    try:
        info = db.get_message_info(user)
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500
    return info, 200

def receive_messages_user(user, sender):
    if user == None:
        return "You are currently not logged in.", 403
    # check sender and receive messages
    try:
        if not db.user_exists(sender):
            return f"{sender} does not exists.", 404
        mids, messages = db.get_messages(user, sender)
        # delete messages from db (buffer)
        db.delete_messages(mids)
    except (DBConnectionError, DBInternalError) as e:
        return f"Database Error: {e}", 500
    return messages, 200
