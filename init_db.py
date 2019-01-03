#!/usr/bin/env python
from sqlalchemy import create_engine

from models import BASE

ENGINE = create_engine('postgres:///domain_blacklist')
BASE.metadata.drop_all(ENGINE)
BASE.metadata.create_all(ENGINE)
