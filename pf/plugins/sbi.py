from pathlib import Path
import csv
from datetime import datetime

import pandas as pd
import numpy as np

from ..types.models import Account, Record

BANK_NAME = "State Bank Of India"
SUPPORTED_FORMATS = ["csv", "xls"]


def _get_metadata(file: Path):
    account = {
        Account.bank_name.name: BANK_NAME,
    }

    skiprows = 0
    start_date = None
    end_date = None

    with open(file, "r") as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.reader(f, delimiter=":", dialect=dialect)
        for row_num, row in enumerate(reader):
            if len(row) == 0:
                continue
            k = row[0].strip()
            if k == "Account Number":
                account[Account.account_number.column_name] = row[1].strip().strip("_")
            elif k == "IFS (Indian Financial System) Code":
                account[Account.ifsc.column_name] = row[1].strip()
            elif k == "Account Description":
                account[Account.description.column_name] = row[1].strip()
            elif k == "Account Name":
                account[Account.primary_holder.column_name] = row[1].strip()
            elif k == "Start Date":
                start_date = datetime.strptime(row[1].strip(), "%d %b %Y")
            elif k == "End Date":
                end_date = datetime.strptime(row[1].strip(), "%d %b %Y")
            elif k.startswith("Txn Date"):
                skiprows = row_num
                break

    return (account, start_date, end_date, skiprows)


def get_metadata(file: Path):
    (account, start_date, end_date, _) = _get_metadata(file)
    return (account, start_date, end_date)


def import_statement(file: Path, display_file_name=None):

    (account, start_date, end_date, skiprows) = _get_metadata(file)

    df = pd.read_csv(
        file,
        sep=" *\t *",
        skiprows=skiprows,
        skipfooter=2,
        engine="python",
        thousands=",",
        usecols=[
            "Txn Date",
            "Description",
            "Ref No./Cheque No.",
            "Debit",
            "Credit",
            "Balance",
        ],
    )

    df = df[
        [
            "Txn Date",
            "Description",
            "Ref No./Cheque No.",
            "Debit",
            "Credit",
            "Balance",
        ]
    ]

    df = df.rename(
        columns={
            "Txn Date": Record.date.name,
            "Description": Record.description.name,
            "Ref No./Cheque No.": Record.txn_reference.name,
            "Debit": Record.debit.name,
            "Credit": Record.credit.name,
            "Balance": Record.balance.name,
        }
    )

    df[Record.date.name] = pd.to_datetime(df[Record.date.name], format="%d %b %Y")
    df[Record.date.name] = df[Record.date.name].apply(lambda x: str(x))

    for i in [Record.debit.name, Record.credit.name, Record.balance.name]:
        df[i] = pd.to_numeric(df[i]).replace({np.nan: None})

    df[Record.fk_account_number.column_name] = account[
        Account.account_number.column_name
    ]
    df[Record.imported_file.column_name] = (
        display_file_name if display_file_name else file.name
    )
    df[Record.imported_order.column_name] = df.index

    txns = df.to_dict(orient="records")

    return (account, txns, start_date, end_date)
