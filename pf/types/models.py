from peewee import (
    SqliteDatabase,
    TextField,
    DateTimeField,
    SQL,
    Model,
    ForeignKeyField,
    FloatField,
    BlobField,
    DateField,
    fn,
)
from pathlib import Path

_db = SqliteDatabase(None)


def init_db(db_path: Path):
    _db.init(db_path, pragmas={"journal_mode": "wal", "foreign_keys": 1})
    with _db:
        _db.create_tables([Account, Record, AccountStatement], safe=True)
    return _db


class BaseModel(Model):
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

    @classmethod
    def get_accounts_and_statements(cls):
        accounts = list(Account.select().dicts())
        for a in accounts:
            a["statements"] = list(
                AccountStatement.select(
                    AccountStatement.filename,
                    fn.strftime("%d-%m-%Y", AccountStatement.start),
                    fn.strftime("%d-%m-%Y", AccountStatement.end),
                )
                .where(AccountStatement.fk_account_number == a["account_number"])
                .order_by(AccountStatement.start)
                .dicts()
            )
        return accounts


class AccountStatement(BaseModel):
    fk_account_number = ForeignKeyField(Account)
    start = DateField()
    end = DateField()
    filename = TextField(unique=True)
    file_content = BlobField()

    @classmethod
    def has_statement(cls, filename):
        return (
            AccountStatement.select(AccountStatement.filename)
            .where(AccountStatement.filename == filename)
            .count()
            == 1
        )


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
