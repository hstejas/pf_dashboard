<script>
import Chart from 'chart.js/auto';
import { Line } from 'vue-chartjs';
import '@fortawesome/fontawesome-free/css/all.min.css';
import "bulma"
import AccountDetails from './AccountDetails.vue';
import SortableTable from './SortableTable.vue';
import { url_for } from "../utils/base_path.js"

export default {
    components: {
        AccountDetails,
        SortableTable,
        Line,
    },
    props: {
    },
    data() {
        return {
            accounts: [],
            selected_account: null,
            filters: "",
            chart: {
                data: null,
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
            },
            txn: {
                columns: [
                    {
                        name: "date",
                        display_name: "Date",
                        width: "10%",
                    },
                    {
                        name: 'credit',
                        display_name: "Credit",
                        formatter: (cell) => this.to_rupee(cell),
                        width: "12%",
                        align: "right",
                    },
                    {
                        name: 'debit',
                        display_name: "Debit",
                        formatter: (cell) => this.to_rupee(cell),
                        width: "12%",
                        align: "right",
                    },
                    {
                        name: 'balance',
                        display_name: "Balance",
                        formatter: (cell) => this.to_rupee(cell),
                        width: "12%",
                        align: "right",
                    },
                    {
                        name: "description",
                        display_name: "Description",
                    }
                ],
                rows: [],
            }
        }
    },
    methods: {
        url_for,
        to_rupee(value) {
            if (value === null) {
                return null;
            }
            value = (value).toLocaleString(
                undefined,
                { minimumFractionDigits: 2 }
            );
            return `₹ ${value}`;
        },
        refresh_chart() {
            const params = new URLSearchParams({
                account: this.selected_account.account_number,
                filters: this.filters
            }).toString();
            fetch(url_for("/api/transactions/?") + params)
                .then((resp) => resp.json())
                .then((data) => {
                    this.chart.data = {}
                    this.chart.data.datasets = data.datasets;
                    this.chart.options.plugins.title.text = data.accounts;
                    this.txn.rows = data.transactions;
                })
                .catch((resp) => console.log(resp))
        }
    },
    mounted() {
        fetch(url_for("/api/accounts/"))
            .then((resp) => resp.json())
            .then((data) => {
                this.accounts = data;
            });
    }
}
</script>

<template>
    <div class="section">
        <div class="columns">
            <div class="column is-2">
                <div class="field-group">
                    <div class="field">
                        <label class="label">Account Number</label>
                        <div class="control has-icons-left">
                            <div class="select">
                                <select v-model="selected_account" required>
                                    <option disabled :value="null">Select Account Number</option>
                                    <option v-for="acc in accounts" :value="acc">{{ acc.account_number }}</option>
                                </select>
                            </div>
                            <span class="icon is-left has-text-primary">
                                <i class="fa-solid fa-circle-user"></i>
                            </span>
                            <a :href="url_for('/accounts/')">Manage Accounts</a>
                        </div>
                        <div class="field">
                            <div id="account_details"></div>
                            <AccountDetails v-if="selected_account" :bank="selected_account.bank_name"
                                :account_number="selected_account.account_number"
                                :primary_holder="selected_account.primary_holder"
                                :description="selected_account.description"></AccountDetails>
                        </div>
                        <div class="field">
                            <label class="label">Filter keywords</label>
                            <div class="control">
                                <textarea v-model="filters" class="textarea has-fixed-size"
                                    placeholder="'|' separated keywords to filter by. e.g 'amazon|flipkart|water'"></textarea>
                            </div>
                        </div>
                        <div class="field">
                            <div class="control">
                                <div class="buttons has-addons">
                                    <button id="clear" class="button">Clear</button>
                                    <button @click="refresh_chart" class="button is-success">Refresh</button>
                                </div>
                            </div>
                        </div>
                        <div class="field">
                            <label class="label">Quick Filters</label>
                            <div class="control">
                                <div class="buttons">
                                    <button id="add_shopping" class="button">Shopping</button>
                                    <button id="add_medical" class="button">Medical</button>
                                    <button id="add_salary" class="button">Salary</button>
                                    <button id="add_groceries" class="button">Salary</button>
                                    <button id="add_food" class="button">Food Delivery</button>
                                    <button id="add_utilities" class="button">Utilities</button>
                                    <button id="add_bill_payment" class="button">Bill payments</button>
                                    <button id="add_fuel" class="button">Fuel</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="column">
                <div class="section" v-if="chart.data">
                    <Line :data="chart.data" :options="chart.options"></Line>
                </div>
                <div class="section" v-if="txn.rows.length > 0">
                    <SortableTable :columns="txn.columns" :rows="txn.rows"></SortableTable>
                </div>
            </div>
        </div>
    </div>
</template>