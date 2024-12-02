from fastapi import FastAPI
app = FastAPI(root_path="/api")

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from .sql import env_init
sql_engine = create_engine(
                "mysql://"+env_init.MYSQL_USER+":"+env_init.MYSQL_PASSWORD+"@localhost/"+env_init.MYSQL_DB,
                isolation_level="READ UNCOMMITTED",poolclass=NullPool
                )

from . import views_api