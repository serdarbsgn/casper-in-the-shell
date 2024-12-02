from datetime import datetime,timedelta
from html import escape
from fastapi import Form,Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.sql.sql_queries import Select

from app.sql.sql_connection import sqlconn

from app.sql.tables import User
from app.main import app
import bcrypt
from app.utils import generate_jwt_token

class MsgResponse(BaseModel):
    msg : str
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    sanitized_errors = []
    for error in exc.errors():
        # Sanitize input by removing 'input' key
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
    return MsgResponse(msg = "You have been helped.")#Obviously placeholder

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
