from models.base import Base
from models.database import engine


def initialize_schema():
    Base.metadata.create_all(engine)
