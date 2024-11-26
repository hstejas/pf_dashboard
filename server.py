#!/bin/env python
from flask import Flask, request, render_template
import pandas as pd
from pf.types.models import Account, Record, init_db
from playhouse.flask_utils import FlaskDB
from pf.plugins.utils import log
from numpy import nan, polyfit


def create_app():
    DATABASE = "pf.db"
    app = Flask(__name__)
    peewee_db = init_db(DATABASE)
    FlaskDB(app, peewee_db)
    return app


app = create_app()


def filter_description(df: pd.DataFrame, filters: str):
    if len(filters) < 2:
        return df
    if filters[0] == "~":
        return df[~df.description.str.contains(filters[1:], case=False)]
    return df[df.description.str.contains(filters, case=False)]


@app.route("/")
def index():
    accounts = list(Account.select(Account.bank_name, Account.account_number).dicts())
    print(accounts)
    return render_template("index.jinja", accounts=accounts)


@app.route("/accounts/")
def accounts():
    return render_template("accounts.jinja")


@app.route("/transactions/")
def transactions():
    account = request.args.get("account")
    filters = request.args.get("filters", "")
    res = list(
        Record.select(
            Record.date,
            Record.description,
            Record.txn_reference,
            Record.credit,
            Record.debit,
            Record.balance,
        )
        .where(Record.fk_account_number ** f"%{account}%")
        .dicts()
    )
    df = pd.DataFrame(data=res).fillna("")
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_values(by="date")

    df = filter_description(df, filters)

    return df.to_html()


@app.route("/api/accounts/")
def api_accounts():
    # res = list(Account.select().dicts())
    res = Account.get_accounts_and_statements()
    # df = pd.DataFrame(data=res)
    return res


def extrapolate_balance_for_loan(accounts, balance_df, samples=12):
    if "loan" in accounts.lower() and len(balance_df) > samples:
        # y = a*x^2 + b*x + c
        coeff = polyfit(
            balance_df.index[-samples:].map(lambda x: x.timestamp()),
            balance_df["balance"][-samples:],
            2,
        )
        log.debug(coeff)

        def extrapolate(x):
            return (coeff[0] * x * x) + (coeff[1] * x) + coeff[2]

        ep_df = []
        for date, _ in balance_df[-samples:].iterrows():
            ep_df.append([date, extrapolate(date.timestamp())])
        for i in range(5 * 12 + 2):
            if ep_df[-1][1] >= 0:
                break
            next = ep_df[-1][0] + pd.DateOffset(months=1)
            ep_df.append([next, extrapolate(next.timestamp())])
        ep_df = pd.DataFrame(ep_df, columns=["date", "balance"]).set_index("date")
        ep_df.index = ep_df.index.strftime("%Y-%m")
        return ep_df
    return None


@app.route("/api/transactions/")
def api_transactions():
    account = request.args.get("account")
    filters = request.args.get("filters", "")

    accounts = ", ".join(
        [
            f"{acc.account_number} - {acc.description}"
            for acc in Account.select().where(Account.account_number ** f"%{account}%")
        ]
    )

    res = list(
        Record.select(
            Record.date, Record.description, Record.credit, Record.debit, Record.balance
        )
        .where(Record.fk_account_number ** f"%{account}%")
        .order_by(Record.date, Record.imported_order)
        .dicts()
    )
    if len(res) == 0:
        return "Not found", 404

    df = pd.DataFrame(data=res)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    df = filter_description(df, filters)
    df = df.replace(to_replace=nan, value=None)

    group = df.groupby(pd.Grouper(freq="ME"))
    gdf = group[["credit", "debit"]].sum()
    # gdf = gdf.replace(to_replace=nan, value=None)
    gdf.index = gdf.index.strftime("%Y-%m")
    balance_df = group[["balance"]].mean()
    balance_df = balance_df.replace(to_replace=nan, value=None)

    ep_df = extrapolate_balance_for_loan(accounts, balance_df)

    balance_df.index = balance_df.index.strftime("%Y-%m")

    table_df = df[["description", "credit", "debit"]]
    table_df.index = table_df.index.strftime("%Y-%m")
    table_df = table_df.reset_index()

    ret = {
        "accounts": accounts,
        "datasets": [
            {
                "label": "credit",
                "data": gdf["credit"].to_dict(),
            },
            {
                "label": "debit",
                "data": gdf["debit"].to_dict(),
            },
        ],
        "transactions": table_df.to_dict(orient="records"),
    }

    if len(balance_df) > 0:
        ret["datasets"].append(
            {
                "label": "avg balance",
                "data": balance_df["balance"].to_dict(),
            }
        )

    if ep_df is not None and len(ep_df) > 0:
        ret["datasets"].append(
            {
                "label": "balance trend",
                "data": ep_df["balance"].to_dict(),
                "borderDash": [1, 5],
            }
        )

    return ret


if __name__ == "__main__":
    app.run(port=3000, debug=True)
