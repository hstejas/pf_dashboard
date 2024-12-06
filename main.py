#!/bin/env python

from pf.types.models import Account, Record, AccountStatement, init_db, _db

from pathlib import Path
import glob
from importlib import import_module
import hashlib

from pf.plugins.utils import log

if __name__ == "__main__":
    init_db("pf.db")
    dirs = glob.glob("data/*")
    for d in dirs:
        files = glob.glob(f"{d}/*")
        name = Path(d).name
        if name.startswith(".") or name.startswith("_"):
            continue
        import_statement = getattr(
            import_module(f"pf.plugins.{name}"), "import_statement"
        )
        for f in files:
            f = Path(f)
            if AccountStatement.has_statement(f.name):
                log.info(f"File '{f}' is already processed")
                continue

            log.info(f"Processing file '{f}'")
            (acc, txns, start_date, end_date) = import_statement(f)
            with _db:
                Account.get_or_create(**acc)
                content = f.read_bytes()
                AccountStatement.create(
                    fk_account_number=acc["account_number"],
                    start=start_date,
                    end=end_date,
                    filename=f.name,
                    sha256=hashlib.sha256(content).hexdigest(),
                    file_content=content,
                )
                Record.insert_many(txns).execute()
