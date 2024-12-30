<script>
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bulma'
import { url_for } from "../utils/base_path.js"

export default {
    emits: ["refresh"],
    props: {
        stmt_id: [String, Number],
        filename: String,
        start: String,
        end: String,
    },
    methods: {
        url_for,
        deleteStatement() {
            fetch(url_for(`/api/statements/${this.stmt_id}/`), { method: 'DELETE' })
                .then((resp) => { this.$emit("refresh") })
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
            <a class="button" id="download" :href="url_for(`/api/statements/${stmt_id}/`)">
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