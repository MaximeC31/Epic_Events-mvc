import bcrypt

from models.collaborator import Collaborator


def hash_password(password: str) -> str:
    password_error = Collaborator.check_password(password)
    if password_error:
        raise ValueError(password_error)

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )
    return password_hash.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if Collaborator.check_password(password):
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False
