<script>
import "bulma"
import AccountRow from "./AccountRow.vue"
import ImportFileModal from "./ImportFileModal.vue"
import { url_for } from "../utils/base_path.js"

export default {
    components: {
        AccountRow,
        ImportFileModal,
    },
    data() {
        return {
            accounts: [],
            import_file_modal_active: false,
        }
    },
    methods: {
        url_for,
        load_account_details() {
            fetch(url_for("/api/accounts/"))
                .then((resp) => resp.json())
                .then((data) => {
                    this.accounts = data;
                })
        }
    },
    mounted() {
        this.load_account_details();
    },
};
</script>



<template>
    <ImportFileModal :is_active="import_file_modal_active" @close="import_file_modal_active = false"
        @refresh="load_account_details"></ImportFileModal>
    <div class="section">
        <div>
            <div class="buttons has-addons">
                <a class="button is-primary" :href="url_for('/')">
                    <span class="icon">
                        <i class="fas fa-home"></i>
                    </span>
                    <span>
                        Home
                    </span>
                </a>
                <a id="show_import_file_modal" class="button" @click="import_file_modal_active = true">
                    <span class="icon">
                        <i class="fas fa-file-import"></i>
                    </span>
                    <span>
                        Import Statement
                    </span>
                </a>

                <a class="button" :href="url_for('/api/statements')">
                    <span class="icon">
                        <i class="fas fa-download"></i>
                    </span>
                    <span>
                        Download Statement Bundle
                    </span>
                </a>
                <a class="button is-danger" href="">
                    <span class="icon">
                        <i class="fas fa-file-zipper"></i>
                    </span>
                    <span>
                        Import Statement Bundle
                    </span>
                </a>
                <a class="button is-danger" :href="url_for('/api/reset')">
                    <span class="icon">
                        <i class="fas fa-trash"></i>
                    </span>
                    <span>
                        Full Reset
                    </span>
                </a>
            </div>
        </div>
        <div class="section">
            <AccountRow v-for="a in accounts" :bank="a.bank_name" :account_numer="a.account_numer"
                :name="a.primary_holder" :description="a.description" :statements="a.statements"
                @refresh="load_account_details">
            </AccountRow>
        </div>
    </div>
</template>