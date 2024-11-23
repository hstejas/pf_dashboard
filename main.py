#!/bin/env python

from pf.types.models import Account, Record, init_db

from pathlib import Path
import glob
from importlib import import_module

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
            (acc, txns) = import_statement(Path(f))
            Account.get_or_create(**acc)
            Record.insert_many(txns).execute()
