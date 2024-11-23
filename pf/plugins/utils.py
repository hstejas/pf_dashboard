import logging

log = logging.getLogger("PF")
logging.basicConfig(level=logging.DEBUG)

PASSWORD_FILE = "data/.passwords"

logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)


def get_passwords() -> list:
    with open(PASSWORD_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]
