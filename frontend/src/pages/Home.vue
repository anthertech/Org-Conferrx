<template>
  <Navbar />
  <div v-if="eventData">
    <Banner :event="eventData" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { createResource } from 'frappe-ui';
import Navbar from '../component/Navbar.vue';
import Banner from '../component/Banner.vue';

const eventLoading = ref(true); // Loading state

// Fetch the event data
const event = createResource({
  url: 'e_desk.e_desk.api.frontend_api.default_confer',
  method: 'GET',
  auto: true,
  onSuccess() {
    eventLoading.value = false; // Mark loading as complete
  }
});

// Only pass data once it's fully loaded
let eventData = computed(() => {
  if (!eventLoading.value && event.data && typeof event.data === 'object') {
    return event.data;
  }
  return null; // Return null if data is not yet available
});
</script>