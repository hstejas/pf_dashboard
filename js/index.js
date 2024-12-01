import Chart from 'chart.js/auto';
import { Grid } from "gridjs";
import "gridjs/dist/theme/mermaid.css";
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bulma'


function create_account_row(bank_name, account_number, name, description, statements) {
    const account_row = document.getElementById('account_row').content.cloneNode(true);
    account_row.querySelector('#bank').textContent = bank_name;
    account_row.querySelector('#account_number').textContent = account_number;
    account_row.querySelector('#name').textContent = name;
    account_row.querySelector('#description').textContent = description;
    return account_row;
}

function get_all_accounts() {
    fetch("/api/accounts/")
        .then((resp) => resp.json())
        .then((data) => {
            let accounts = document.getElementById("account")
            for (let a of data) {
                accounts.options[accounts.options.length] = new Option(a.account_number, JSON.stringify(a));
            }
        })
}


function show_account_details() {
    const details = JSON.parse(document.getElementById("account").value);
    const out = document.getElementById("account_details");

    out.innerHTML = ''
    out.appendChild(create_account_row(
        details.bank_name,
        details.account_number,
        details.primary_holder,
        details.description
    ));
}


function to_rupee(value) {
    if (value === null) {
        return null;
    }
    return `₹ ${value}`;
}


function refresh_chart() {
    const params = new URLSearchParams({
        account: JSON.parse(document.getElementById('account').value).account_number,
        filters: document.getElementById('filters').value
    }).toString();
    fetch("/api/transactions/?" + params)
        .then((resp) => resp.json())
        .then((data) => {
            chart.data.datasets = data.datasets;
            chart.options.plugins.title.text = data.accounts;
            chart.update();
            txn_grid.updateConfig({
                fixedHeader: true,
                pagination: true,
                // height: "80vh",
                search: true,
                sort: true,
                autoWidth: true,
                className: {
                    table: 'table is-hoverable is-striped is-bordered',
                    th: 'is-primary'
                },
                columns: [
                    {
                        name: "date",
                        sort: true
                    },
                    {
                        name: 'credit',
                        formatter: (cell) => to_rupee(cell)
                    },
                    {
                        name: 'debit',
                        formatter: (cell) => to_rupee(cell)
                    },
                    {
                        name: "description",
                        width: '60%'
                    }
                ],
                data: data.transactions
            }).forceRender();
        })
        .catch((resp) => console.log(resp))
}


const txn_grid = new Grid({ data: [] }).render(document.getElementById("wrapper"));

const ctx = document.getElementById('myChart');
var chart = new Chart(ctx, {
    type: 'line',
    options: {
        plugins: {
            title: {
                display: true,
                font: {
                    size: 24,
                    weight: 'bold'
                },
            }
        }
    }
})

document.getElementById('clear').onclick = () => { 
    document.getElementById('filters').value = "";
};
document.getElementById('refresh').onclick = refresh_chart;
document.getElementById("account").onchange = show_account_details;
document.addEventListener('DOMContentLoaded', get_all_accounts);


