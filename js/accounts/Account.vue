<script>
import "bulma"
import AccountRow from "./AccountRow.vue"
import ImportFileModal from "./ImportFileModal.vue"
import {ref} from "vue"

const importFileModalRef = ref()

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
    },
    mounted() {
        fetch("/api/accounts/")
            .then((resp) => resp.json())
            .then((data) => {
                this.accounts = data;
            })
    },
};
</script>



<template>
    <ImportFileModal :is_active="import_file_modal_active" @close="import_file_modal_active = false"></ImportFileModal>
    <div class="section">
        <div>
            <div class="buttons has-addons">
                <a class="button is-primary" href="/">
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

                <a class="button" href="/api/statements">
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
                <a class="button is-danger" href="/api/reset">
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
                :name="a.primary_holder" :description="a.description" :statements="a.statements">
            </AccountRow>
        </div>
    </div>
</template>