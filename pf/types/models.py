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
    AutoField,
)
from pathlib import Path

_db = SqliteDatabase(None)


def init_db(db_path: Path):
    _db.init(db_path, pragmas={"journal_mode": "wal", "foreign_keys": 1})
    create_tables()
    return _db


def create_tables():
    with _db:
        _db.create_tables([Account, Record, AccountStatement], safe=True)


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
                    AccountStatement.id,
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
    id = AutoField()
    fk_account_number = TextField()  # Should map to Record.account_number, but loosely
    start = DateField()
    end = DateField()
    filename = TextField(unique=True)
    sha256 = TextField(unique=True)
    file_content = BlobField()

    @classmethod
    def get_file_by_id(cls, id):
        try:
            res = cls.select(cls.filename, cls.file_content).where(cls.id == id).get()
        except Exception:
            return (None, None)
        return (res.filename, res.file_content)

    @classmethod
    def get_all_files(cls):
        res = cls.select(cls.filename, cls.file_content)
        return [(r.filename, r.file_content) for r in res]

    @classmethod
    def has_statement(cls, filename):
        return cls.select(cls.filename).where(cls.filename == filename).count() == 1

    @classmethod
    def delete_by_id(cls, id):
        stmt = cls.select().where(cls.id == id).get()
        Record.delete_by_statement(stmt.filename, stmt.fk_account_number)
        cls.delete().where(cls.id == id).execute()


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

    @classmethod
    def delete_by_statement(cls, statement, account):
        cls.delete().where(
            cls.imported_file == statement, cls.fk_account_number == account
        ).execute()
