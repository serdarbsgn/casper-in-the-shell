from html import escape

from fastapi import Form, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.main import app
from app.sql.sql_connection import sqlconn
from app.sql.sql_queries import Insert, Select
from app.sql.tables import Command, Macro, User
from app.utils import check_auth, listify
from app.views_api import MsgResponse


@app.get("/commands",
        summary="Search",
        description="Search for the command",
        responses={
        200: {
            "description": "Return latest matching command",
            "model": MsgResponse
        },401:{
            "description": "Show unauthorized message(Jwt doesn't exist, or expired.)",
        }
        })
def search_command(keyword: str = Query("", description="Keyword to search for, leaving it empty will return the latest command(s) you saved."),
                limit: int = Query(0, description="Limit of returned commands, starting from latest, leaving this 0 will return all commands that keyword matches."),
                jwt:str = Query(description="Jwt used for auth."),
                include_ids:bool = Query(False,description="Include id numbers of commands in the result(to help create macros)")):
    auth = check_auth(jwt)
    if not auth:
        return JSONResponse(content={"detail": "Can't get the user because token is expired or wrong."}, status_code=401)
    with sqlconn() as sql:
        query_data = {"user_id":auth["user"]}
        if limit > 0:
            query_data["limit"] = limit
        if keyword:
            query_data["keyword"] = keyword
        if include_ids:
            query_data["include_ids"] = include_ids
        commands = listify(sql.session.execute(Select.command(query_data)).fetchall())
        return JSONResponse(content={"msg": commands}, status_code=200)
    
@app.post("/commands",
        summary="Save a command",
        description="Save the command supplied by user.",
        responses={
        200: {
            "description": "Return success message.",
            "model": MsgResponse
        },401:{
            "description": "Show unauthorized message(Jwt doesn't exist, or expired.)",
        },400:{
            "description": "Bad request, command is empty or just whitespaces.",
        }
        })
def save_command(command: str = Form("",max_length=511),jwt:str = Query(description="Jwt used for auth.")):
    auth = check_auth(jwt)
    if not auth:
        return JSONResponse(content={"detail": "Can't get the user because token is expired or wrong."}, status_code=401)
    if not command:
        return JSONResponse(content={"detail": "You wouldn't want to insert an empty command."}, status_code=400)
    with sqlconn() as sql:
        #can also add a check if command already exists, this only matters informing the user though, skipped for now.
        sql.session.execute(Insert.command({"user_id": auth["user"],"command": command}))
        sql.session.commit()
        return MsgResponse(msg = f"I managed to save your command. {command}")

@app.get("/macro",
        summary="Search a macro",
        description="Search the macro name supplied by user.",
        responses={
        200: {
            "description": "Return success message.",
            "model": MsgResponse
        },401:{
            "description": "Show unauthorized message(Jwt doesn't exist, or expired.)",
        }
        })
def search_macro(name: str = Query("", description="Name to search for, leaving it empty will return the latest macro you saved."),
                jwt:str = Query(description="Jwt used for auth.")):
    auth = check_auth(jwt)
    if not auth:
        return JSONResponse(content={"detail": "Can't get the user because token is expired or wrong."}, status_code=401)
    with sqlconn() as sql:
        query_data = {"user_id":auth["user"]}
        if name:
            query_data["name"] = name
        commands = sql.session.execute(Select.macro(query_data)).scalars().fetchall()
        return JSONResponse(content={"msg": commands}, status_code=200)
    
@app.get("/macros",
        summary="Retrieve all macro names",
        description="Retrieve all macro names previously saved by this user.",
        responses={
        200: {
            "description": "Return success message.",
            "model": MsgResponse
        },401:{
            "description": "Show unauthorized message(Jwt doesn't exist, or expired.)",
        }
        })
def fetch_macros(jwt:str = Query(description="Jwt used for auth.")):
    auth = check_auth(jwt)
    if not auth:
        return JSONResponse(content={"detail": "Can't get the user because token is expired or wrong."}, status_code=401)
    with sqlconn() as sql:
        query_data = {"user_id":auth["user"]}
        macros = sql.session.execute(Select.macros(query_data)).scalars().fetchall()
        return JSONResponse(content={"msg": macros}, status_code=200)
    
@app.post("/macro",
        summary="Save a macro",
        description="Save the macro supplied by user.",
        responses={
        200: {
            "description": "Return success message.",
            "model": MsgResponse
        },401:{
            "description": "Show unauthorized message(Jwt doesn't exist, or expired.)",
        },400:{
            "description": "Bad request, macro is empty or just whitespaces or macro name already exists/commands have incorrect command id in it",
        }
        })
def save_macro(name: str = Form(max_length=255),commands: str = Form("",max_length=255) ,jwt:str = Query(description="Jwt used for auth.")):
    auth = check_auth(jwt)
    if not auth:
        return JSONResponse(content={"detail": "Can't get the user because token is expired or wrong."}, status_code=401)
    if not commands:
        return JSONResponse(content={"detail": "You wouldn't want to insert an empty macro."}, status_code=400)
    with sqlconn() as sql:
        query_data = {"user_id":auth["user"],"name":name}
        exist_check = sql.session.execute(Select.macro_exists(query_data)).fetchall()
        if exist_check:
            return JSONResponse(content={"detail": "This macro name already exists"}, status_code=400)
        command_ids = [int(cmd_id.strip()) for cmd_id in commands.replace(",", " ").split() if cmd_id.strip()]
        macro = Macro(user_id = auth["user"],name = escape(name))
        sql.session.add(macro)
        sql.session.flush()
        insert_data = []
        for order,command_id in enumerate(command_ids,start=1):
            insert_data.append({"macro_id":macro.id,"command_id":command_id,"order":order})
        if sql.execute(Insert.macro_command(insert_data)):
            sql.session.commit()
            return MsgResponse(msg = f"I managed to save your macro.")
        else:
            return JSONResponse(content={"detail": "You probably entered incorrect command id in the macro"}, status_code=400)