from sqlalchemy import  delete, func, literal, select, update,desc,not_,exists
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.mysql import insert
from app.sql.tables import *
from sqlalchemy.sql.functions import coalesce,concat,count

class Select():
    def user(data):
        return select(User).where(User.username == data["username"])
    
    def command(data):
        query = select(Command.command).where(Command.user_id == data["user_id"]).order_by(Command.id.desc())
        if "include_ids" in data:
            query = select(Command.id,Command.command).where(Command.user_id == data["user_id"]).order_by(Command.id.desc())
        if "keyword" in data:
            query = query.where(Command.command.ilike("%"+data["keyword"]+"%"))
        if "limit" in data:
            query = query.limit(data["limit"])
        return query
    
    def macro(data):
        subquery = None
        if "name" in data:
            subquery = select(Macro.id).where(Macro.user_id == data["user_id"], Macro.name == data["name"]).subquery()
        else:
            subquery = select(Macro.id).where(Macro.user_id == data["user_id"]).order_by(Macro.id.desc()).limit(1).subquery()
        command_ids_subquery = select(MacroCommand.command_id).where(MacroCommand.macro_id.in_(subquery)).order_by(MacroCommand.order).subquery()
        return select(Command.command).where(Command.id.in_(command_ids_subquery))
    def macro_exists(data):
        return select(Macro.id).where(Macro.user_id == data["user_id"], Macro.name == data["name"])
    
    def macros(data):
        return select(Macro.name).where(Macro.user_id == data["user_id"])
    
class Insert():
    def command(data):
        #using on_duplicate_key_update prevents headaches about unique constraint exceptions, 
        # we just update id with its original value as fallback.
        return insert(Command).values(data).on_duplicate_key_update(id = Command.id)
    
    def macro_command(data):
        return insert(MacroCommand).values(data).on_duplicate_key_update(macro_id = MacroCommand.macro_id)