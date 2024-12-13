<script>
import "bulma"

export default {
    props: {
        bank: String,
        account_number: String,
        primary_holder: String,
        description: String,
    },
}

</script>

<template>
    <div class="box">
        <div><span>{{ bank }}</span></div>
        <div><span>{{ account_number }}</span></div>
        <div><span>{{ primary_holder }}</span></div>
        <div><span>{{ description }}</span></div>
    </div>
</template>
