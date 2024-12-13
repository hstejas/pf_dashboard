<script>
import '@fortawesome/fontawesome-free/css/all.min.css';
import "bulma"

export default {
    props: {
        is_active: {
            type: Boolean,
            required: true,
        }
    },
    data() {
        return {
            banks: [],
            import_plugin: null,
            import_files: null,
            error: null,
        };
    },
    methods: {
        close() {
            this.error = null;
            this.$emit('close')
        },
        show_selected_file(elem) {
            this.import_files = elem.target.files;
            this.error = null;
        },
        import_statement() {
            if (this.import_files === null || this.import_plugin === null) {
                this.error = "Select file and bank";
                return;
            }
        }
    },
    mounted() {
        fetch("/api/supported/")
            .then((data) => data.json())
            .then((data) => {
                this.banks = data;
            });
    }
}

</script>

<template>
    <div :class="{ 'is-active': is_active }" class="modal">
        <div @click="close" class="modal-background"></div>
        <div class="modal-card">
            <header class="modal-card-head">
                <p class="modal-card-title">Upload an account statement</p>
                <button @click="close" class="modal-close is-large" aria-label="close"></button>
            </header>
            <div class="modal-card-body">
                <div class="notification is-danger" v-if="error !== null"> {{ error }} </div>
                <div class="field">
                    <label class="label">Bank</label>
                    <div class="control">
                        <div class="select" @change="error = null">
                            <select v-model="import_plugin">
                                <option disabled :value="null">Select a bank</option>
                                <option v-for="bank in banks" :value="bank.id">{{ bank.display_name }}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="field">
                    <label class="label">Select a file</label>
                    <div class="file has-name">
                        <label class="file-label">
                            <input class="file-input" type="file" name="file" @change="show_selected_file" />
                            <span class="file-cta">
                                <span class="file-icon">
                                    <i class="fas fa-upload"></i>
                                </span>
                                <span class="file-label"> Choose a file… </span>
                            </span>
                            <span v-if="import_files" class="file-name">{{ import_files[0].name }}</span>
                        </label>
                    </div>
                </div>
            </div>
            <footer class="modal-card-foot">
                <div class="buttons has-addons">
                    <button class="button is-primary" type="submit" @click="import_statement">Upload File</button>
                    <button class="button" @click="close">Cancel</button>
                </div>
            </footer>
        </div>
    </div>
</template>