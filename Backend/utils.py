from hashlib import sha256

def hash_pw(pw):
    return sha256(pw.encode('utf-8')).hexdigest()
