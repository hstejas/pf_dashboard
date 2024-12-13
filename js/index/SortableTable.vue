<script>
import '@fortawesome/fontawesome-free/css/all.min.css';
import "bulma"

export default {
    props: {
        columns: {
            type: Array,
            required: true,
        },
        rows: {
            type: Array,
            required: true,
        },
    },
    data() {
        return {
            sort: {
                column: null,
                direction: null,
            },
            search_string: "",
        };
    },
    computed: {
        sortedAndFilteredRows() {
            filtered_rows = this.rows
            if (this.search_string.length > 0) {
                lc_search = this.search_string.toLowerCase();
                filtered_rows = this.rows.filter((value) => {
                    for (var key in value) {
                        if (String(value[key]).toLowerCase().includes(lc_search)) {
                            return true
                        }
                    }
                    return false;
                });
            }

            if (this.sort.column === null) {
                return filtered_rows;
            }
            return filtered_rows.sort((a, b) => {
                const aValue = a[this.sort.column];
                const bValue = b[this.sort.column];

                if (this.sort.direction === 'asc') {
                    if (aValue < bValue) return -1;
                    if (aValue > bValue) return 1;
                } else {
                    if (aValue < bValue) return 1;
                    if (aValue > bValue) return -1;
                }

                return 0;
            });
        },
    },
    methods: {
        sortBy(column) {
            if (this.sort.column === column.name) {
                if (this.sort.direction == 'asc') {
                    this.sort.direction = 'desc';
                }
                else if (this.sort.direction == 'desc') {
                    this.sort.direction = null;
                    this.sort.column = null;
                }
            } else {
                this.sort.column = column.name;
                this.sort.direction = 'asc';
            }
        },
    },
};
</script>

<style>
.caret {
    display: inline-block;
    width: 0;
    height: 0;
    margin-left: 2px;
    vertical-align: middle;
    border-top: 4px solid;
    border-right: 4px solid transparent;
    border-left: 4px solid transparent;
}

.caret-asc {
    border-bottom: none;
    border-top: 4px solid #333;
}

.caret-desc {
    border-top: none;
    border-bottom: 4px solid #333;
}
</style>

<template>
    <div class="field">
        <label class="label">Filter</label>
        <div class="control has-icons-left">
            <input class="input" type="text" placeholder="Filter Text" v-model="search_string" />
            <span class="icon is-left has-text-primary">
                <i class="fa-solid fa-user"></i>
            </span>
        </div>
    </div>
    <div class="table-container">
        <table class="table is-fullwidth">
            <thead>
                <tr>
                    <th v-for="(column, index) in columns" :key="index" @click="sortBy(column)"
                        :style="{ width: column.width }"
                        :class='{ "has-text-right": column.align == "right", "has-text-left": column.align == "left" }'>
                        {{ column.display_name }}
                        <span v-if="sort.column === column.name"
                            :class="{ 'caret': true, 'caret-asc': sort.direction === 'asc', 'caret-desc': sort.direction === 'desc' }">
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, index) in sortedAndFilteredRows" :key="index">
                    <td v-for="(column, index) in columns" :key="index"
                        :class='{ "has-text-right": column.align == "right", "has-text-left": column.align == "left" }'>
                        {{ column.formatter ? column.formatter(row[column.name]) : row[column.name] }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
