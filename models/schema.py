from models.base import Base
from models.client import Client
from models.collaborator import Collaborator
from models.contract import Contract
from models.database import engine
from models.event import Event


def initialize_schema():
    Base.metadata.create_all(engine)
