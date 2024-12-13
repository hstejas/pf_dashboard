<script>
import '@fortawesome/fontawesome-free/css/all.min.css';
import "bulma"
import StatementRow from './StatementRow.vue'

export default {
    components:{
        StatementRow,
    },
    props: {
        bank: String,
        account_number: String,
        name: String,
        description: String,
        statements: Array,
    },
}
</script>


<template>
    <div class="box">
        <article class="media">
            <figure class="media-left">
                <span class="icon is-large">
                    <i class="fas fa-coins"></i>
                </span>
            </figure>
            <div class="media-content">
                <div class="content">
                    <div class="title is-5"><span>{{bank}}</span></div>
                    <div><strong>Account Number:</strong> <span> {{account_number}}</span></div>
                    <div><strong>Name:</strong> <span>{{name}}</span></div>
                    <div><strong>Description:</strong> <span>{{description}}</span></div>
                    <div v-if="statements.length >= 0">
                        <span class="subtitle is-5">Statements</span>
                        <table class="table">
                            <tr>
                                <th>Statement</th>
                                <th>From</th>
                                <th>To</th>
                                <th>Actions</th>
                            </tr>
                            <StatementRow v-for="s in statements" :stmt_id="s.id" :filename="s.filename" :start="s.start"
                                :end="s.end"></StatementRow>
                        </table>
                    </div>
                </div>
            </div>
        </article>
    </div>
</template>