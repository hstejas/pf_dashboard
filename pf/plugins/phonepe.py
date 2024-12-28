import pandas as pd
from pathlib import Path
from ..types.models import Account, Record
import pypdf
import logging as log
from io import StringIO
from .utils import get_passwords
from datetime import datetime

BANK_NAME = "Phone Pe"
ACC_PREFIX = "phonepe"
SUPPORTED_FORMATS = ["pdf"]


def peek_line(f: StringIO) -> str:
    pos = f.tell()
    line = ""
    try:
        while not line.strip():
            line = f.readline()
            if line == "":
                break
    finally:
        f.seek(pos)
    return line


def decrypt_if_required(pdf: pypdf.PdfReader, file: Path):
    if pdf.is_encrypted:
        passwords = get_passwords()
        decrypted = False
        for p in passwords:
            if pdf.decrypt(p) != pypdf.PasswordType.NOT_DECRYPTED:
                decrypted = True
                break
        if not decrypted:
            raise Exception(f"Password is required for {file}")


def get_metadata(file: Path) -> dict:
    account = {
        Account.bank_name.name: BANK_NAME,
        Account.description.name: "UPI",
    }
    acc_number = None
    start_date = None
    end_date = None
    with pypdf.PdfReader(file) as pdf:
        decrypt_if_required(pdf, file)

        if len(pdf.pages) == 0:
            log.error(f"Empty pdf file {file}")
            raise Exception(f"Empty odf file {file}")

        text = pdf.pages[0].extract_text(extraction_mode="layout")

        sio = StringIO(text)
        line = sio.readline().strip()
        line = line.replace("Transaction Statement for ", "")
        acc_number = f"{ACC_PREFIX}_{line}"
        account[Account.account_number.name] = acc_number
        account[Account.primary_holder.name] = line
        period = sio.readline().strip()  # skip second line
        (s, e) = period.split(" - ")
        start_date = datetime.strptime(s.strip(), "%b %d, %Y")
        end_date = datetime.strptime(e.strip(), "%b %d, %Y")

    return (account, start_date, end_date)


def import_statement(file: Path, display_file_name) -> dict:
    account = {
        Account.bank_name.name: BANK_NAME,
        Account.description.name: "UPI",
    }
    acc_number = None
    start_date = None
    end_date = None
    df = pd.DataFrame()
    with pypdf.PdfReader(file) as pdf:
        decrypt_if_required(pdf, file)

        if len(pdf.pages) == 0:
            log.error(f"Empty pdf file {file}")
            raise Exception(f"Empty odf file {file}")

        for num, page in enumerate(pdf.pages):
            text = page.extract_text(extraction_mode="layout")
            index = text.rfind(f"Page {num+1} of ")
            if index == -1:
                continue
            text = text[0:index]
            sio = StringIO(text)
            if num == 0:
                line = sio.readline().strip()
                line = line.replace("Transaction Statement for ", "")
                acc_number = f"{ACC_PREFIX}_{line}"
                account[Account.account_number.name] = acc_number
                account[Account.primary_holder.name] = line
                period = sio.readline().strip()  # skip second line
                (s, e) = period.split(" - ")
                start_date = datetime.strptime(s.strip(), "%b %d, %Y")
                end_date = datetime.strptime(e.strip(), "%b %d, %Y")
                header = peek_line(sio)
                specs = (
                    (0, header.index("Transaction Details") - 1),
                    (header.index("Transaction Details"), header.index("Type") - 1),
                    (header.index("Type"), header.index("Amount") - 1),
                    (header.index("Amount"), header.index("Amount") + 15),
                )
                df = pd.read_fwf(sio, colspecs=specs)
            else:
                header = peek_line(sio)
                specs = (
                    (0, header.index("Transaction Details") - 1),
                    (header.index("Transaction Details"), header.index("Type") - 1),
                    (header.index("Type"), header.index("Amount") - 1),
                    (header.index("Amount"), header.index("Amount") + 15),
                )
                page_df = pd.read_fwf(sio, colspecs=specs)
                df = pd.concat([df, page_df], ignore_index=True)

    merged_rows = []
    for _, row in df.iterrows():
        if not row.hasnans:
            merged_rows.append(row)
            continue
        for k, v in row.fillna("").items():
            if v:
                merged_rows[-1][k] = merged_rows[-1][k] + " " + v

    for row in merged_rows:
        row[Record.balance.column_name] = None
        row[Record.txn_reference.name] = None
        amount = row["Amount"].replace("INR", "").strip()
        if row["Type"] == "Debit":
            row[Record.debit.column_name] = amount
            row[Record.credit.column_name] = None
        else:
            row[Record.debit.column_name] = None
            row[Record.credit.column_name] = amount

    df = pd.DataFrame(merged_rows)
    df = df.rename(
        columns={
            "Date": Record.date.name,
            "Transaction Details": Record.description.name,
        }
    )
    df = df[
        [
            Record.date.column_name,
            Record.description.column_name,
            Record.txn_reference.column_name,
            Record.debit.column_name,
            Record.credit.column_name,
            Record.balance.column_name,
        ]
    ]

    df[Record.date.name] = pd.to_datetime(
        df[Record.date.name], format="%b %d, %Y %I:%M %p"
    )
    df[Record.date.name] = df[Record.date.name].apply(lambda x: str(x))

    df[Record.debit.name] = pd.to_numeric(df[Record.debit.name])
    df[Record.credit.name] = pd.to_numeric(df[Record.credit.name])
    df[Record.balance.name] = pd.to_numeric(df[Record.balance.name])

    df[Record.fk_account_number.column_name] = acc_number
    df[Record.imported_file.column_name] = (
        display_file_name if display_file_name else file.name
    )
    df[Record.imported_order.column_name] = df.index

    return (account, df.to_dict(orient="records"), start_date, end_date)
