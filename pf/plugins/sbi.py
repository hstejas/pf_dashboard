import pandas as pd
from pathlib import Path
from ..types.models import Account, Record
import csv

BANK_NAME = "State Bank Of India"


def import_statement(file: Path):

    account = {
        Account.bank_name.name: BANK_NAME,
    }

    skiprows = 0
    acc_number = None

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
                acc_number = account[Account.account_number.column_name]
            elif k == "IFS (Indian Financial System) Code":
                account[Account.ifsc.column_name] = row[1].strip()
            elif k == "Account Description":
                account[Account.description.column_name] = row[1].strip()
            elif k == "Account Name":
                account[Account.primary_holder.column_name] = row[1].strip()
            elif k.startswith("Txn Date"):
                skiprows = row_num
                break

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

    df[Record.debit.name] = pd.to_numeric(df[Record.debit.name])
    df[Record.credit.name] = pd.to_numeric(df[Record.credit.name])
    df[Record.balance.name] = pd.to_numeric(df[Record.balance.name])

    df[Record.fk_account_number.column_name] = acc_number
    df[Record.imported_file.column_name] = file.name
    df[Record.imported_order.column_name] = df.index

    txns = df.to_dict(orient="records")

    return (account, txns)