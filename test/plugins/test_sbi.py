from pathlib import Path
from datetime import datetime

import pf.plugins.sbi as sbi
from pf.types.models import Account

ACCOUNT_NO = "00000011111122233"
NAME = "ABCD EFGH"
BRANCH = "XYZ Branch"

FILE_PATH = "./test/plugins/test_sbi_{}.txt"


def test_good_case1():
    data_file = Path(FILE_PATH.format("good_case1"))
    (account, transactions, start_date, end_date) = sbi.import_statement(data_file)
    assert start_date == datetime(2021, 4, 1, 0, 0)
    assert end_date == datetime(2021, 8, 31, 0, 0)
    assert account == {
        Account.description.column_name: "PPF Account",
        Account.account_number.column_name: ACCOUNT_NO,
        Account.primary_holder.column_name: NAME,
        Account.bank_name.name: sbi.BANK_NAME,
    }
    name = data_file.name
    expected_txns = [
        {
            "date": "2021-04-05 00:00:00",
            "description": "DEPOSIT TRANSFER---",
            "txn_reference": "TRANSFER FROM 1234",
            "debit": None,
            "credit": 10000.0,
            "balance": 192226.0,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 0,
        },
        {
            "date": "2021-05-05 00:00:00",
            "description": "DEPOSIT TRANSFER---",
            "txn_reference": "TRANSFER FROM 4444",
            "debit": 10000.00,
            "credit": None,
            "balance": 202226.0,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 1,
        },
        {
            "date": "2021-06-05 00:00:00",
            "description": "DEPOSIT TRANSFER---",
            "txn_reference": "TRANSFER FROM 5555",
            "debit": None,
            "credit": 10000.0,
            "balance": 212226.0,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 2,
        },
        {
            "date": "2021-07-05 00:00:00",
            "description": "DEPOSIT TRANSFER---",
            "txn_reference": "TRANSFER FROM 2222",
            "debit": None,
            "credit": 10000.0,
            "balance": 222226.0,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 3,
        },
        {
            "date": "2021-08-05 00:00:00",
            "description": "DEPOSIT TRANSFER---",
            "txn_reference": "TRANSFER FROM 2345",
            "debit": None,
            "credit": 10000.0,
            "balance": 232226.0,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 4,
        },
        {
            "date": "2021-08-05 00:00:00",
            "description": "DEPOSIT TRANSFER---",
            "txn_reference": "TRANSFER FROM 2346",
            "debit": None,
            "credit": 10000.0,
            "balance": 242226.0,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 5,
        },
    ]

    assert len(transactions) == len(expected_txns)
    assert transactions == expected_txns


def test_good_case2():
    data_file = Path(FILE_PATH.format("good_case2"))
    (account, transactions, start_date, end_date) = sbi.import_statement(data_file)
    assert start_date == datetime(2008, 11, 1, 0, 0)
    assert end_date == datetime(2008, 11, 30, 0, 0)
    assert account == {
        Account.description.column_name: "HOME LOAN",
        Account.account_number.column_name: ACCOUNT_NO,
        Account.primary_holder.column_name: NAME,
        Account.bank_name.name: sbi.BANK_NAME,
    }
    name = data_file.name
    expected_txns = [
        {
            "balance": -133217.0,
            "credit": None,
            "date": "2008-11-30 00:00:00",
            "debit": 1001.0,
            "description": "PART PERIOD INTER---",
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 0,
            "txn_reference": "-",
        },
        {
            "balance": -123217.0,
            "credit": 10000.0,
            "date": "2008-11-24 00:00:00",
            "debit": None,
            "description": "DEPOSIT TRANSFER-Trf From "
            "1234                                                      TRANSFER "
            "FROM 1234                         ABCD EFGH--",
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 1,
            "txn_reference": "-",
        },
        {
            "balance": -113217.0,
            "credit": 10000.0,
            "date": "2008-11-16 00:00:00",
            "debit": None,
            "description": "DEPOSIT TRANSFER-Trf From "
            "1234                                                      TRANSFER "
            "FROM 1234                         ABCD EFGH--",
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 2,
            "txn_reference": "-",
        },
        {
            "balance": -112217.0,
            "credit": 1000.0,
            "date": "2008-11-11 00:00:00",
            "debit": None,
            "description": "O.S. DEPOSIT TRAN-TRANSFER "
            "FROM                                                                                       "
            "TRANSFER FROM 1234                         ABCD EFGH--",
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 3,
            "txn_reference": "-",
        },
        {
            "balance": -111217.0,
            "credit": 1100.0,
            "date": "2008-11-05 00:00:00",
            "debit": None,
            "description": "O.S. DEPOSIT TRAN-TRANSFER "
            "FROM                                                                                       "
            "TRANSFER FROM 1234                         ABCD EFGH--",
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 4,
            "txn_reference": "-",
        },
        {
            "balance": -111111.0,
            "credit": 106.0,
            "date": "2008-11-01 00:00:00",
            "debit": None,
            "description": "DEPOSIT TRANSFER-Trf From "
            "1234                                                       TRANSFER "
            "FROM 1234                         ABCD EFGH--",
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 5,
            "txn_reference": "-",
        },
    ]

    assert len(transactions) == len(expected_txns)
    assert transactions == expected_txns
