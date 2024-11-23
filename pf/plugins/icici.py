import pandas as pd
import xlrd
from pathlib import Path
from ..types.models import Account, Record
from .utils import log


BANK_NAME = "ICICI Bank"


def import_statement(file: Path):
    with xlrd.open_workbook(file) as w:
        sheet = w.sheet_by_index(0)

        account = {
            Account.bank_name.name: BANK_NAME,
        }

        skiprows = 0
        acc_number = None

        for i in range(1, 100):
            row = sheet.row(i)
            k = row[1].value.strip()
            if k == "Account Number":
                (acc_number, primary_holder) = row[3].value.split("-", 2)
                acc_number = acc_number.split("(")[0]
                account[Account.account_number.column_name] = acc_number
                account[Account.primary_holder.column_name] = primary_holder.strip()
                account[Account.description.column_name] = row[3].value.strip()

            elif k.startswith("S No."):
                skiprows = i
                break

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

    df[Record.fk_account_number.column_name] = acc_number
    df[Record.imported_file.column_name] = file.name
    df[Record.imported_order.column_name] = df.index

    txns = df.to_dict(orient="records")

    return (account, txns)
