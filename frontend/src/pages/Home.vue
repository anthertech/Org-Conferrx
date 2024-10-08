<template>


<h1>Check thiss</h1>
</template>

<script setup>
import {createListResource} from "frappe-ui";
import { ref } from 'vue'
import { Dialog } from 'frappe-ui'
import { createResource } from 'frappe-ui'
import { session } from '../data/session'




ConferList = createListResource({
doctype:"Confer",
fields:["name",'start_date'],
auto:true,
onSuccess(data){
console.log(data);
}
})

</script>
