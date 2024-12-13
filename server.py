#!/bin/env python
from flask import Flask, request, render_template, make_response, abort
import pandas as pd
from pf.types.models import Account, AccountStatement, Record, init_db, create_tables
from playhouse.flask_utils import FlaskDB
from pf.plugins.utils import log
from numpy import nan, polyfit
import io
import zipfile
from importlib import import_module
import glob
from pathlib import Path
import tempfile
import hashlib


def create_app():
    DATABASE = "pf.db"
    app = Flask(__name__)
    peewee_db = init_db(DATABASE)
    FlaskDB(app, peewee_db)
    return app, peewee_db


(app, database) = create_app()


def _get_plugins():
    res = {}
    files = glob.glob("pf/plugins/*")
    for f in files:
        f = Path(f)
        if not f.is_file():
            continue
        name = f.stem
        plugin = import_module(f"pf.plugins.{name}")
        if hasattr(plugin, "BANK_NAME"):
            res[name] = plugin
    return res


def filter_description(df: pd.DataFrame, filters: str):
    if len(filters) < 2:
        return df
    if filters[0] == "~":
        return df[~df.description.str.contains(filters[1:], case=False)]
    return df[df.description.str.contains(filters, case=False)]


@app.route("/")
def index():
    return render_template("index.jinja")


@app.route("/accounts/")
def accounts():
    return render_template("accounts.jinja")


@app.route("/api/accounts/")
def api_accounts():
    res = Account.get_accounts_and_statements()
    return res


def extrapolate_balance_for_loan(accounts, balance_df, samples=12):
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


def extrapolate_balance_for_provident_fund(accounts, balance_df, samples=12):
    # y = m*x + c
    coeff = polyfit(
        balance_df.index[-samples:].map(lambda x: x.timestamp()),
        balance_df["balance"][-samples:],
        1,
    )
    log.debug(coeff)

    def extrapolate(x):
        return (coeff[0] * x) + coeff[1]

    ep_df = []
    for date, _ in balance_df[-samples:].iterrows():
        ep_df.append([date, extrapolate(date.timestamp())])
    for i in range(5 * 12):
        next = ep_df[-1][0] + pd.DateOffset(months=1)
        ep_df.append([next, extrapolate(next.timestamp())])
    ep_df = pd.DataFrame(ep_df, columns=["date", "balance"]).set_index("date")
    ep_df.index = ep_df.index.strftime("%Y-%m")
    return ep_df


def extrapolate_balance(accounts, balance_df, samples=12):
    if len(balance_df) <= samples:
        return None
    if "PPF" in accounts:
        return extrapolate_balance_for_provident_fund(accounts, balance_df, samples)
    if "loan" in accounts.lower():
        return extrapolate_balance_for_loan(accounts, balance_df, samples)
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
        .order_by(Record.date.desc(), Record.imported_order.desc())
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
    gdf.index = gdf.index.strftime("%Y-%m")
    balance_df = group[["balance"]].mean()
    balance_df = balance_df.replace(to_replace=nan, value=None)

    ep_df = extrapolate_balance(accounts, balance_df)

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


@app.route("/api/statements/<id>/", methods=["GET"])
def api_get_statement(id):
    (filename, content) = AccountStatement.get_file_by_id(id)
    if filename is None:
        abort(404)

    resp = make_response(content, 200)
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return resp


@app.route("/api/statements/<id>/", methods=["DELETE"])
def api_delete_statement(id):
    AccountStatement.delete_by_id(id)
    return make_response("", 200)


@app.route("/api/statements/", methods=["PUT", "POST"])
def api_upload_statement():
    plugin_id = request.args.get("plugin")
    filename = Path(request.args.get("filename")).name
    content = request.data
    plugins = _get_plugins()
    if plugin_id not in plugins:
        return make_response(f"Unknown plugin '{plugin_id}'", 400)
    if filename == "":
        return make_response(f"Invalid filename '{filename}'", 400)
    if len(content) == 0:
        return make_response("Empty file", 400)

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()
        (acc, txns, start_date, end_date) = plugins[plugin_id].import_statement(
            Path(tmp_file.name)
        )
        with database:
            Account.get_or_create(**acc)
            AccountStatement.create(
                fk_account_number=acc["account_number"],
                start=start_date,
                end=end_date,
                filename=filename,
                sha256=hashlib.sha256(content).hexdigest(),
                file_content=content,
            )
            Record.insert_many(txns).execute()
    return make_response("", 200)


@app.route("/api/reset/", methods=["GET"])
def api_reset():
    with database:
        Record.drop_table()
        AccountStatement.drop_table()
        Account.drop_table()
        create_tables()
    return make_response("", 200)


@app.route("/api/statements/", methods=["GET"])
def api_get_all_statements():
    stmt_list = None
    with database:
        stmt_list = AccountStatement.get_all_files()
    if not stmt_list:
        return make_response("No statements found", 404)
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as z:
        for name, plugin, content in stmt_list:
            z.writestr(f"{plugin}/{name}", content)

    resp = make_response(buffer.getvalue(), 200)
    resp.headers["Content-Disposition"] = 'attachment; filename="statements.zip"'
    return resp


@app.route("/api/supported/", methods=["GET"])
def api_get_supported_list():
    res = []
    for name, plugin in _get_plugins().items():
        res.append(
            {
                "id": name,
                "display_name": plugin.BANK_NAME,
                "supported_formats": plugin.SUPPORTED_FORMATS,
            }
        )
    return res


if __name__ == "__main__":
    app.run(port=3000, debug=False)
