<template>
  <h1>Check this</h1>
</template>

<script setup>
import { ref } from 'vue'
import { Dialog, createListResource } from 'frappe-ui'  // Consolidate imports from frappe-ui
import { session } from '../data/session'

// Declare ConferList using const
const ConferList = createListResource({
  doctype: "Confer",
  fields: ["name", "start_date"],
  auto: true,
  onSuccess(data) {
    console.log(data);
  }
})

</script>
