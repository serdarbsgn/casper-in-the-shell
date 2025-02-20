from datetime import datetime, timedelta
from html import escape

import bcrypt
from fastapi import Form, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from app.main import app
from app.sql.sql_connection import sqlconn
from app.sql.sql_queries import Select
from app.sql.tables import User
from app.utils import generate_jwt_token


class MsgResponse(BaseModel):
    msg : str
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    sanitized_errors = []
    for error in exc.errors():
        # Sanitize output by removing 'input' key returned to user
        sanitized_error = {key: value for key, value in error.items() if key != "input"}
        sanitized_errors.append(sanitized_error)
    return JSONResponse(
        status_code=422,
        content={"detail": sanitized_errors},
    )

@app.get("/",
        summary="Help",
        description="Show help message",
        responses={
        200: {
            "description": "Show help message",
            "model": MsgResponse
        }
        })
def help():
    return PlainTextResponse("""
                            ~~~Consider using cins.py rather than curl to interact with the api~~~
    /login POST:
        Example Usage:
        curl -X POST http://localhost:8002/api/login -d 'username=username&password=password'
        Returns response JSON:
        HTML 200: {"msg":"jwt"}
        HTML 422: Json message about the error (Username and password needs to be between certain lengths, or they are not supplied, or they are not strings.)
        HTML 400: {"detail": "Credentials are invalid."}

    /register POST:
        Example Usage:
        curl -X POST http://localhost:8002/api/register -d 'username=username&password=password'
        Returns response JSON:
        HTML 200: {"msg":"You are registered now, yay!"}
        HTML 422: Json message about the error (Username and password needs to be between certain lengths, or they are not supplied, or they are not strings.)
        HTML 400: {"detail": "Username already exists."}

    /commands GET:
        Example Usage:
        curl -X GET http://localhost:8002/api/commands?keyword={kw_string}&limit={integer}&include_ids={boolean}&jwt={jwt}

        Returns the commands matching query, in LIFO order. Latest command is returned first.
        keyword can be empty but it needs to be included as a query,
        limit defines the returned command count, not including or setting it to 0 returns all findings.
        include_ids sets the format data is returned, not including or setting to false returns command strings as an array,
          while setting it to true returns array of [id,command_string] which is useful for setting up macros. 
        jwt is the jwt key returned from /login endpoint.

        Returns response JSON:
        HTML 200: {"msg":"["command2","command1"]"} or if include_ids set to True {"msg":"[[5,"command2"],[3,"command1"]]"}
        HTML 422: Json message about the error
        HTML 401: {"detail": "Show unauthorized message(Jwt doesn't exist, or expired.)"}

    /commands POST:
        Example Usage:
        curl -X POST http://localhost:8002/api/commands?jwt={jwt} -d 'command={command}'

        command is the command you want to be saved.
        jwt is the jwt key returned from /login endpoint.

        Returns response JSON:
        HTML 200: {"msg":"I managed to save your command. {command}"}
        HTML 422: Json message about the error
        HTML 400: {"detail": "Bad request, command is empty or just whitespaces."}
        HTML 401: {"detail": "Show unauthorized message(Jwt doesn't exist, or expired.)"}

    /macros GET:
        Example Usage:
        curl -X GET http://localhost:8002/api/macros?jwt={jwt}

        Returns the macro names saved by the user identified by jwt.
        jwt is the jwt key returned from /login endpoint.

        Returns response JSON:
        HTML 200: {"msg":"["macroname1","macroname2"]"}
        HTML 401: {"detail": "Show unauthorized message(Jwt doesn't exist, or expired.)"}    
        
    /macro GET:
        Example Usage:
        curl -X GET http://localhost:8002/api/macro?jwt={jwt}&name={name}

        Returns the commands saved by the user identified by jwt bundled together under a macro name.
        name is the given name of the macro by the user.
        jwt is the jwt key returned from /login endpoint.

        Returns response JSON:
        HTML 200: {"msg":"["command1","command4","command5"]"}  eg macro saved as "1,4,5"
        HTML 401: {"detail": "Show unauthorized message(Jwt doesn't exist, or expired.)"}  

    /macro POST:
        Example Usage:
        curl -X GET http://localhost:8002/api/macro?jwt={jwt} -d "name={macro_name}&commands={command_ids}"

        Saves a macro with a user defined name using comma seperated command_ids.
        macro_name defines the macro name, leaving this empty will return the latest saved macro.
        command_ids is a string, eg "1,4,5" will save a commands that corresponds to the command strings 
        that is returned from using /commands GET endpoint with include_id's query set to True
        jwt is the jwt key returned from /login endpoint.

        Returns response JSON:
        HTML 200: {"msg":"I managed to save your macro."}
        HTML 401: {"detail": "Show unauthorized message(Jwt doesn't exist, or expired.)"}
        HTML 400: {"detail": "Bad request, macro is empty or just whitespaces or macro name already 
        exists/commands have incorrect command id in it"}
""")

@app.post("/login",
        summary="Login",
        description="Show login message",
        responses={
        200: {
            "description": "Return login dialog.",
            "model": MsgResponse
        },400:{
            "description": "Invalid credentials",
        }
        })
def login(username: str = Form(...,min_length=4,max_length=31),password: str = Form(...,min_length=8)):
    username = escape(username)
    password_bytes = bytes(password,"utf-8")
    with sqlconn() as sql:
        user_exists = sql.session.execute(Select.user({"username":username})).scalars().all()
        if not user_exists:
            return JSONResponse(content={"detail": "Credentials are invalid."}, status_code=400)
        if not bcrypt.checkpw(password_bytes,bytes(user_exists[0].password,"utf-8")): 
            return JSONResponse(content={"detail": "Credentials are invalid."}, status_code=400)
        expire_at = str(datetime.now()+timedelta(hours=4))
        auth_jwt_token = generate_jwt_token({"expire_at":expire_at,"user":user_exists[0].id})
        return MsgResponse(msg = auth_jwt_token)

@app.post("/register",
        summary="Register",
        description="Show register message",
        responses={
        200: {
            "description": "Return register success dialog.",
            "model": MsgResponse
        },400:{
            "description": "Show unauthorized message(Username already exists aka db based errors.)",
        }
        })
def register(username: str = Form(...,min_length=4,max_length=31),password: str = Form(...,min_length=8)):
    username = escape(username)
    with sqlconn() as sql:
        user_exists = sql.session.execute(Select.user({"username":username})).mappings().fetchall()
        if user_exists:
            return JSONResponse(content={"detail": "Username already exists."}, status_code=400)
        password_bytes = bytes(password,"utf-8")
        hashed_pw = bcrypt.hashpw(password_bytes,bcrypt.gensalt())
        user = User(username = username,password = hashed_pw)
        sql.session.add(user)
        sql.session.commit()
        return MsgResponse(msg ="You are registered now, yay!")

from app import views_funcs
