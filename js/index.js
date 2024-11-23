import Chart from 'chart.js/auto';
import { Grid } from "gridjs";
import "gridjs/dist/theme/mermaid.css";
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bulma'

function to_rupee(value) {
    if (value === null) {
        return null;
    }
    return `₹ ${value}`;
}


function refresh_chart() {
    const params = new URLSearchParams({
        account: document.getElementById('account').value,
        filters: document.getElementById('filters').value
    }).toString();
    fetch("/transactions/plot?" + params)
        .then((resp) => resp.json())
        .then((data) => {
            chart.data.datasets = data.datasets;
            chart.options.plugins.title.text = data.accounts;
            chart.update();
            txn_grid.updateConfig({
                fixedHeader: true,
                pagination: true,
                height: "80vh",
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
document.getElementById('refresh').onclick = refresh_chart;


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