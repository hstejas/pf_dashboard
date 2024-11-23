from peewee import (
    SqliteDatabase,
    TextField,
    DateTimeField,
    SQL,
    Model,
    ForeignKeyField,
    FloatField,
)
from pathlib import Path

_db = SqliteDatabase(None)


def init_db(db_path: Path):
    _db.init(db_path, pragmas={"journal_mode": "wal", "foreign_keys": 1})
    with _db:
        _db.create_tables([Account, Record], safe=True)
    _db.close()
    return _db


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = _db


class Account(BaseModel):
    account_number = TextField(null=False, unique=True, primary_key=True)
    primary_holder = TextField(null=False)
    bank_name = TextField(null=True)
    bank_branch = TextField(null=True)
    ifsc = TextField(null=True)
    customer_id = TextField(null=True)
    description = TextField()
    curreny = TextField(null=False, default="INR")
    country = TextField(default="India")


class Record(BaseModel):
    fk_account_number = ForeignKeyField(Account)
    date = DateTimeField(null=False)
    credit = FloatField(null=True)
    debit = FloatField(null=True)
    balance = FloatField(null=True)
    description = TextField()
    txn_reference = TextField(null=True)
    imported_file = TextField()
    imported_order = TextField()

    class Meta:
        constraints = [SQL("UNIQUE (imported_file, imported_order) ON CONFLICT IGNORE")]
