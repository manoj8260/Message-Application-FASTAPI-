import uuid
from sqlmodel import SQLModel,Field ,Column
from sqlalchemy.dialects import postgresql as pg
from datetime import datetime


class User(SQLModel,table=True):
    __tablename__ ='users'
    uid :uuid.UUID =  Field(
        default_factory= uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True) , primary_key=True,nullable=False)
    )
    username :str
    email : str
    name : str 
    password : str =  Field(nullable=False,exclude= True)
    is_active : bool = Field(default=False)
    role : str = Field(
        default='user',
        sa_column=Column(pg.VARCHAR,server_default='user',nullable=False))
    created_at : datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True),default =datetime.utcnow))
    updated_at : datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True),default =datetime.utcnow,onupdate=datetime.utcnow))
    