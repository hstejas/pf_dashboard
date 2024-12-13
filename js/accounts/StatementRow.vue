<script>
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bulma'

export default {
    props: {
        stmt_id: [String, Number],
        filename: String,
        start: String,
        end: String,
    },
    methods: {
        deleteStatement() {
            fetch(`/api/statements/${this.stmt_id}/`, { method: 'DELETE' })
                .then((resp) => { console.log(resp) })
                .catch((data) => { alert(data); });
        }
    }
}
</script>

<template>
    <tr>
        <td>{{ filename }}</td>
        <td>{{ start }}</td>
        <td>{{ end }}</td>
        <td id="actions">
            <a class="button" id="download" :href="`/api/statements/${stmt_id}/`">
                <span class="icon has-text-info">
                    <i class="fas fa-download"></i>
                </span>
            </a>
            <a class="button" @click="deleteStatement">
                <span class="icon has-text-danger">
                    <i class="fas fa-trash"></i>
                </span>
            </a>
        </td>
    </tr>
</template>