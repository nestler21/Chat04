import requests
import json
import uuid
import datetime as dt

from datetime import datetime
from exceptions import *


HEADERS = {"apiKey": "1892",
           "Content-Type": "application/json"}
IP = "14.0.8.4"
BASE_URL = f"http://{IP}:8080"

### Accounts

def user_exists(username):
    url = BASE_URL + f"/user/exists/{username}"    
    try:
        response = requests.get(url=url, headers=HEADERS)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    if response.status_code == 200:
        if json.loads(response.text):
            return True
        else:
            return False
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}") 

def create_user(username, password):
    url = BASE_URL + "/user/create"
    data = json.dumps({"username": username, "password": password})
    try:
        response = requests.post(url=url, headers=HEADERS, data=data)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 201:
        return True
    elif response.status_code == 409:
        return False
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}") 

def delete_user(username):
    url = BASE_URL + f"/user/delete/{username}"    
    try:
        response = requests.delete(url=url, headers=HEADERS)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    if response.status_code == 200:
        return
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}")

def password_correct(username, password):
    url = BASE_URL + f"/user/password"
    data = json.dumps({"username": username, "password": password})
    try:
        response = requests.post(url=url, headers=HEADERS, data=data)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 200:
        if json.loads(response.text):
            return True
        else:
            return False
    elif response.status_code == 404:
        return False
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}") 

### Sessions

def create_session(username):
    max_retries = 5 # adjustable but there shouldn't really be any retries since the uuids should be unique
    retry_counter = 0
    while True:
        retry_counter += 1
        url = BASE_URL + "/session/create"
        sid = str(uuid.uuid1())
        data = json.dumps({"sid": sid,"username": username})
        try:
            response = requests.post(url=url, headers=HEADERS, data=data)
        except requests.exceptions.ConnectionError as e:
            raise DBConnectionError(e)
        
        if response.status_code == 201:
            return sid
        elif response.status_code == 409:
            if retry_counter <= max_retries:
                continue  # try new sid on conflict
            else:
                raise DBInternalError("Unexpected IntegrityError when creating new session")
        elif response.status_code == 500:
            raise DBInternalError(response.text)
        else:
            raise DBInternalError(f"Unexpected Status Code: {response.status_code}")

def get_user_from_sid(sid):
    url = BASE_URL + f"/session/{sid}"
    try:
        response = requests.get(url=url, headers=HEADERS)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 200:
        return json.loads(response.text)
    elif response.status_code == 404:
        return None
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}")

def delete_session(username):
    url = BASE_URL + f"/session/delete/{username}"
    try:
        response = requests.delete(url=url, headers=HEADERS)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 200:
        return
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}")

### Messages

def send_message(message, sender, receiver):
    url = BASE_URL + "/messages/create"
    timestamp = datetime.now() + dt.timedelta(days=1)
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    data = json.dumps({"message": message, "receiver": receiver, "sender": sender, "timestamp": timestamp})
    try:
        response = requests.post(url=url, headers=HEADERS, data=data)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 201:
        return True
    elif response.status_code == 404:
        False  # False implies that the receiver was not found
    elif response.status_code == 400:
        raise InternalServerError(response.text)
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}") 

def get_message_info(username):
    url = BASE_URL + f"/messages/{username}"
    try:
        response = requests.get(url=url, headers=HEADERS)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 200:
        return json.loads(response.text)
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}")
    
def get_messages(username, sender):
    url = BASE_URL + f"/messages/{username}/{sender}"
    try:
        response = requests.get(url=url, headers=HEADERS)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    
    if response.status_code == 200:
        messages_res = json.loads(response.text)
        mids = [message["mid"] for message in messages_res]
        messages = [{"message": message["message"], "timestamp": message["timestamp"]} for message in messages_res]
        return mids, messages
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}")
    
def delete_messages(mids):
    url = BASE_URL + f"/messages/delete"
    data = json.dumps(mids)
    try:
        response = requests.post(url=url, headers=HEADERS, data=data)
    except requests.exceptions.ConnectionError as e:
        raise DBConnectionError(e)
    if response.status_code == 200:
        return
    elif response.status_code == 500:
        raise DBInternalError(response.text)
    else:
        raise DBInternalError(f"Unexpected Status Code: {response.status_code}")
