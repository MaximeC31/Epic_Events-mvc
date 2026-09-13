from models.base import Base
from models.client import Client
from models.collaborator import Collaborator
from models.database import engine


def initialize_schema():
    Base.metadata.create_all(engine)
