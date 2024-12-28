from pathlib import Path
from datetime import datetime

import pf.plugins.canara_bank as cb
from pf.types.models import Account

ACCOUNT_NO = "0111111222333"
NAME = "ABCD EFGH"
BRANCH = "XYZ Branch"
IFSC = "CNRB0000001"
CUSTOMER_ID = "12345678"

FILE_PATH = "./test/plugins/test_canara_bank_{}.txt"


def test_good_case1():
    data_file = Path(FILE_PATH.format("good_case1"))
    (account, transactions, start_date, end_date) = cb.import_statement(
        data_file, data_file.name
    )
    assert start_date == datetime(2002, 1, 1, 0, 0)
    assert end_date == datetime(2002, 2, 1, 0, 0)
    assert account == {
        Account.description.column_name: "SOME PRODUCT",
        Account.account_number.column_name: ACCOUNT_NO,
        Account.primary_holder.column_name: NAME,
        Account.bank_name.name: cb.BANK_NAME,
        Account.ifsc.name: IFSC,
        Account.curreny.name: "INR",
        Account.customer_id.column_name: CUSTOMER_ID,
    }
    name = data_file.name
    expected_txns = [
        {
            "date": "2002-01-04 21:45:15",
            "description": "UPI/abcd/xyz",
            "txn_reference": "0001111",
            "debit": 18.0,
            "credit": None,
            "balance": 20510.52,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 0,
        },
        {
            "date": "2002-01-08 17:58:12",
            "description": "UPI/abcd/xyz",
            "txn_reference": "0002222",
            "debit": 147.00,
            "credit": None,
            "balance": 20363.52,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 1,
        },
        {
            "date": "2002-01-12 17:25:54",
            "description": "UPI/abcd/xyz@#$%^&!",
            "txn_reference": "003333",
            "debit": 344.0,
            "credit": None,
            "balance": 20019.52,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 2,
        },
        {
            "date": "2002-01-16 01:12:12",
            "description": "AAABBBCCC",
            "txn_reference": "",
            "debit": None,
            "credit": 775.0,
            "balance": 20794.52,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 3,
        },
        {
            "date": "2002-01-16 13:50:35",
            "description": "UPI/abcd/xyz",
            "txn_reference": "004444",
            "debit": 480.0,
            "credit": None,
            "balance": 20314.52,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 4,
        },
        {
            "date": "2002-01-19 18:27:24",
            "description": "UPI/abcd/xyz",
            "txn_reference": "005555",
            "debit": 1411.0,
            "credit": None,
            "balance": 18903.52,
            "fk_account_number_id": ACCOUNT_NO,
            "imported_file": name,
            "imported_order": 5,
        },
    ]

    assert len(transactions) == len(expected_txns)
    assert transactions == expected_txns
