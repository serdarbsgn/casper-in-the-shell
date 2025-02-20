from datetime import datetime

import jwt

from .sql.env_init import JWT_SECRET_KEY


def decode_jwt_token(encoded_content):
    try:
        decoded_content = jwt.decode(encoded_content, JWT_SECRET_KEY, ["HS256"])
    except:
        decoded_content = False
    return decoded_content

def generate_jwt_token(content):
    encoded_content = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")
    token = str(encoded_content)
    return token

def check_auth(token):
    test = decode_jwt_token(token)
    if test:
        if not set(["expire_at", "user"]) == set(test.keys()):
            return None
        if datetime.now() < datetime.strptime(test["expire_at"],"%Y-%m-%d %H:%M:%S.%f"):
            return test
    return None

def listify(map):
    templist = []
    for row in map:
        listx = []
        for val in row:
            listx.append(val)
        templist.append(listx)
    return templist