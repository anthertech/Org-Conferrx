<template>
  <div class="w-screen h-screen overflow-hidden flex items-center justify-center">
    <Spinner v-if="eventLoading" class="w-4/6 h-4/6" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { createResource, Spinner } from 'frappe-ui';
import { useRouter } from 'vue-router'; // Correct import

const eventLoading = ref(true); // Loading state

const router = useRouter(); // Initialize router

// Fetch the event data
const event = createResource({
  url: 'e_desk.e_desk.api.frontend_api.default_confer',
  method: 'GET',
  auto: true,
  onSuccess(data) {
    const jsonString = JSON.stringify(data);
    localStorage.setItem('myObject', jsonString);
    eventLoading.value = false; // Mark loading as complete
    router.push({ name: 'Event', params: { id: data.name } }); // Navigate to the desired route
  }
});
</script>

<style>
  circle .spinner-path {
    color: green !important;
  }
</style>