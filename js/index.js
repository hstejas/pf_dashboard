// import Chart from 'chart.js/auto';
// import { Grid } from "gridjs";
// import "gridjs/dist/theme/mermaid.css";
// import '@fortawesome/fontawesome-free/css/all.min.css';
// import 'bulma'


// 


// document.getElementById('clear').onclick = () => { 
//     document.getElementById('filters').value = "";
// };
// document.getElementById('refresh').onclick = refresh_chart;
// document.getElementById("account").onchange = show_account_details;
// document.addEventListener('DOMContentLoaded', get_all_accounts);


import Account from "./index/Index.vue";
import { createApp } from "vue";

createApp(Account).mount('#app')