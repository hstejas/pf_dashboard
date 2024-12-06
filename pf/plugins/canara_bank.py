import pandas as pd
from pathlib import Path
from datetime import datetime
import csv
from ..types.models import Account, Record

BANK_NAME = "Canara Bank"
SUPPORTED_FORMATS = ["csv"]


def _clean(value):
    if not isinstance(value, str):
        return value
    if value.startswith('="') and value.endswith('"'):
        return value[2:-1].strip()
    return value.strip()


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
        reader = csv.reader(f, delimiter=",", dialect=dialect)
        for row_num, row in enumerate(reader):
            if len(row) == 0:
                continue
            if (
                len(row) == 3
                and row[0].strip() == ""
                and row[1].strip() == ""
                and row[2].strip().endswith("Account Statement")
            ):
                account[Account.description.column_name] = _clean(row[2])
            elif row[0] == "Account Number":
                account[Account.account_number.column_name] = _clean(row[1])
            elif row[0] == "IFSC Code":
                account[Account.ifsc.column_name] = _clean(row[1])
            elif row[0] == "Product Name":
                account[Account.description.column_name] = _clean(row[1])
            elif row[0] in ["Account Holders Name", "Account Holder's Name"]:
                account[Account.primary_holder.column_name] = _clean(row[1])
            elif row[0] == "Account Currency":
                account[Account.curreny.column_name] = _clean(row[1])
            elif row[0] == "Customer Id":
                account[Account.customer_id.column_name] = _clean(row[1])
            elif row[0] == "Searched By":
                (start, end) = _clean(row[1]).split(" To ")
                start = start.replace("From ", "").strip()
                end = end.strip()
                fmt = "%d-%b-%Y" if "-" in start else "%d %b %Y"
                start_date = datetime.strptime(start.replace("From ", "").strip(), fmt)
                end_date = datetime.strptime(end.strip(), fmt)
            elif row[0] == "Txn Date" or row[0] == "Transaction Date":
                skiprows = row_num
                break

    return (account, start_date, end_date, skiprows)


def get_metadata(file: Path):
    (account, start_date, end_date, _) = _get_metadata(file)
    return (account, start_date, end_date)


def import_statement(file: Path):

    (account, start_date, end_date, skiprows) = _get_metadata(file)

    df = pd.read_csv(
        file,
        sep=",",
        skiprows=skiprows,
        engine="python",
        thousands=",",
    )

    if "Cheque No." not in df.columns:
        df["Cheque No."] = None

    col_mapping = {}
    for c in df.columns:
        if c in ["Txn Date", "Transaction Date"]:
            col_mapping[c] = Record.date.name
        elif c in ["Description"]:
            col_mapping[c] = Record.description.name
        elif c in ["Cheque No."]:
            col_mapping[c] = Record.txn_reference.name
        elif c in ["Debit"]:
            col_mapping[c] = Record.debit.name
        elif c in ["Credit"]:
            col_mapping[c] = Record.credit.name
        elif c in ["Balance"]:
            col_mapping[c] = Record.balance.name

    df = df.rename(columns=col_mapping)
    df = df[[v for k, v in col_mapping.items()]]

    df = df.map(lambda x: _clean(x))
    df[Record.date.name] = pd.to_datetime(
        df[Record.date.name], format="%d-%m-%Y %H:%M:%S"
    )
    df[Record.date.name] = df[Record.date.name].apply(lambda x: str(x))

    df[Record.debit.name] = pd.to_numeric(df[Record.debit.name])
    df[Record.credit.name] = pd.to_numeric(df[Record.credit.name])
    df[Record.balance.name] = pd.to_numeric(df[Record.balance.name])

    df[Record.fk_account_number.column_name] = account[
        Account.account_number.column_name
    ]
    df[Record.imported_file.column_name] = file.name
    df[Record.imported_order.column_name] = df.index

    txns = df.to_dict(orient="records")

    return (account, txns, start_date, end_date)
