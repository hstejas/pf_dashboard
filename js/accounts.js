import { Grid } from "gridjs";
import "gridjs/dist/theme/mermaid.css";
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bulma'


function create_statement_row(id, filename, start, end) {
    const statement_row = document.getElementById('statement_row').content.cloneNode(true);
    statement_row.querySelector('#filename').textContent = filename;
    statement_row.querySelector('#start').textContent = start;
    statement_row.querySelector('#end').textContent = end;
    statement_row.querySelector('#download').href = `/api/statements/${id}/`;
    return statement_row
}

function create_account_row(bank_name, account_number, name, description, statements) {
    const account_row = document.getElementById('account_row').content.cloneNode(true);
    account_row.querySelector('#bank').textContent = bank_name;
    account_row.querySelector('#account_number').textContent = account_number;
    account_row.querySelector('#name').textContent = name;
    account_row.querySelector('#description').textContent = description;
    const filesList = account_row.querySelector('#statements');
    for (s of statements) {
        const listItem = create_statement_row(s.id, s.filename, s.start, s.end);
        filesList.appendChild(listItem);
    }
    return account_row;
}

function get_all_accounts() {
    fetch("/api/accounts/")
        .then((resp) => resp.json())
        .then((data) => {
            for (let a of data) {
                row = create_account_row(a.bank_name, a.account_number, a.primary_holder, a.description, a.statements)
                document.getElementById("wrapper").appendChild(row);
            }
        })
}

// const txn_grid = new Grid({ data: [] }).render(document.getElementById("wrapper"));

document.addEventListener('DOMContentLoaded', get_all_accounts);
