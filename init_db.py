#!/usr/bin/env python
from models import Base
from sqlalchemy import create_engine

engine = create_engine('postgres:///domain_blacklist')
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
