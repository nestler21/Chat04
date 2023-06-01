import sqlite3
import re

from flask import make_response


def db_query(query):
    connector = sqlite3.connect("Chat_DB.db")
    cursor = connector.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connector.commit()
    connector.close()
    return result

def post_user_create(body):
    username = body.get("username")
    password = body.get("password")
    try:
        db_query(f"""
            INSERT INTO users (username, password)
            VALUES("{username}", "{password}");
        """)
        return 'New user Created.', 201
    except sqlite3.IntegrityError:
        return 'Username is already in use.', 409
    except Exception as e:
        return e, 500
        
def delete_user_delete(username):
    try:
        db_query(f"""
            DELETE FROM users
            WHERE username = "{username}";
        """)
        return 'User deleted.', 200
    except Exception as e:
        return e, 500

def get_user_exists(username):
    try:
        usernames = db_query(f"""
            SELECT username
            FROM users
            WHERE username = "{username}";
        """)
        if len(usernames) == 0:
            return False, 200
        else:
            return True, 200
    except Exception as e:
        return e, 500
    
def post_user_password(body):
    username = body.get("username")
    password = body.get("password")
    try:
        password_query = db_query(f"""
            SELECT password
            FROM users
            WHERE username = "{username}";
        """)
        print(password_query[0][0])
        if len(password_query) == 0:
            return "Username not found.", 404
        elif password_query[0][0] == password:
            return True, 200
        else:
            return False, 200
    except Exception as e:
        return e, 500

def post_session_create(body):
    sid = body.get("sid")
    username = body.get("username")
    try:
        db_query(f"""
            INSERT INTO sessions (sid, username)
            VALUES("{sid}", "{username}");
        """)
        return 'New session created.', 201
    except sqlite3.IntegrityError as e:
        return f"SessionId already in use.", 409
    except Exception as e:
        return e, 500

def delete_session_delete(username):
    try:
        db_query(f"""
            DELETE FROM sessions
            WHERE username = "{username}";
        """)
        return 'Session deleted.', 200
    except Exception as e:
        return e, 500

def get_session(sid):
    try:
        usernames = db_query(f"""
                        SELECT username
                        FROM sessions
                        WHERE sid = "{sid}"
                    """)
        if len(usernames) == 0:
            return "SessionId not found.", 404
        print(usernames[0][0])
        return usernames[0][0], 200
    except Exception as e:
        return e, 500

def post_messages_create(body):
    sender = body.get("sender")
    receiver = body.get("receiver")
    message = body.get("message")
    timestamp = body.get("timestamp")
    # required format of timestamp string: "%Y-%m-%d %H:%M:%S"
    pattern = re.compile("(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})")
    if not pattern.match(timestamp):
        return "Bad format of the timestamp.", 400
    try:
        db_query(f"""
                INSERT INTO messages (sender, receiver, message, timestamp)
                VALUES ("{sender}", "{receiver}", "{message}", "{timestamp}")
            """)
        return "New message created.", 201
    except sqlite3.IntegrityError as e:
        return "Receiver not found.", 404
    except Exception as e:
        return e, 500
    
def post_messages_delete(body):
    mids = body
    try:
        for mid in mids:
            db_query(f"""
                    DELETE FROM messages
                    WHERE mid = "{mid}";
                """)
        return "Messages deleted.", 200
    except Exception as e:
        return e, 500

def get_messages_info(receiver):
    try:
        users = db_query(f"""
            SELECT sender, count(*)
            FROM messages
            WHERE receiver = "{receiver}"
            GROUP BY sender;
        """)
        u_list = [{"sender": u[0], "count": u[1]} for u in users]
        res = make_response(u_list, 200)
        return res
    except Exception as e:
        return e, 500

def get_messages(sender, receiver):
    try:
        messages = db_query(f"""
            SELECT mid, message, timestamp
            FROM messages
            WHERE sender = "{sender}" AND receiver = "{receiver}"
            ORDER BY timestamp;
        """)
        list = [{"mid": m[0], "message": m[1], "timestamp": m[2]} for m in messages]
        res = make_response(list, 200)
        return res
    except Exception as e:
        return e, 500
