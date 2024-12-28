import pandas as pd
import xlrd
from pathlib import Path
from datetime import datetime
from ..types.models import Account, Record
from .utils import log


BANK_NAME = "ICICI Bank"
SUPPORTED_FORMATS = ["xls"]


def _get_metadata(file: Path):
    with xlrd.open_workbook(file) as w:
        sheet = w.sheet_by_index(0)

        account = {
            Account.bank_name.name: BANK_NAME,
        }

        skiprows = 0
        start_date = None
        end_date = None

        for i in range(1, 100):
            row = sheet.row(i)
            k = row[1].value.strip()
            if k == "Account Number":
                (acc_number, primary_holder) = row[3].value.split("-", 2)
                account[Account.account_number.column_name] = acc_number.split("(")[0]
                account[Account.primary_holder.column_name] = primary_holder.strip()
                account[Account.description.column_name] = row[3].value.strip()
            if k == "Transaction Date from":
                if row[3].value == "":
                    continue
            if k == "Transaction Period":
                period = row[3].value
                if period == "":
                    continue
                if period.startswith("FY "):
                    (s, e) = period.replace("FY ", "").split(" - ")
                    start_date = datetime.strptime(f"01 Apr {s}", "%d %b %Y")
                    end_date = datetime.strptime(f"31 Mar {s[0:2]}{e}", "%d %b %Y")
            elif k.startswith("S No."):
                skiprows = i
                break

    return (account, start_date, end_date, skiprows)


def get_metadata(file: Path):
    (account, start_date, end_date, _) = _get_metadata(file)
    return (account, start_date, end_date)


def import_statement(file: Path, display_file_name=None):

    (account, start_date, end_date, skiprows) = _get_metadata(file)

    df = pd.read_excel(
        file,
        skiprows=skiprows,
        usecols=[
            "Transaction Date",
            "Transaction Remarks",
            "Cheque Number",
            "Withdrawal Amount (INR )",
            "Deposit Amount (INR )",
            "Balance (INR )",
        ],
    )
    df = df.rename(
        columns={
            "Transaction Date": Record.date.name,
            "Transaction Remarks": Record.description.name,
            "Cheque Number": Record.txn_reference.name,
            "Withdrawal Amount (INR )": Record.debit.name,
            "Deposit Amount (INR )": Record.credit.name,
            "Balance (INR )": Record.balance.name,
        }
    )

    log.debug("Nulls: %s", df[df["date"].isna()].to_csv())
    df = df[~df[Record.date.name].isna()]
    df[Record.date.name] = pd.to_datetime(df[Record.date.name], format="%d/%m/%Y")
    df[Record.date.name] = df[Record.date.name].apply(lambda x: str(x))

    df[Record.debit.name] = pd.to_numeric(df[Record.debit.name])
    df[Record.credit.name] = pd.to_numeric(df[Record.credit.name])
    df[Record.balance.name] = pd.to_numeric(df[Record.balance.name])

    df[Record.fk_account_number.column_name] = account[
        Account.account_number.column_name
    ]
    df[Record.imported_file.column_name] = (
        display_file_name if display_file_name else file.name
    )
    df[Record.imported_order.column_name] = df.index

    txns = df.to_dict(orient="records")

    return (account, txns, start_date, end_date)
