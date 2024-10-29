<template>
    <div class="h-[75px] ">
        <Navbar />
    </div>
    <div v-if="eventData">
      <Banner :event="eventData" />
    </div>
  </template>
  
<script setup>
    import { computed, ref } from 'vue';
    import { createResource } from 'frappe-ui';
    import Navbar from '../component/Navbar.vue';
    import Banner from '../component/Banner.vue';
    import { useRoute } from 'vue-router';
    const route = useRoute();

    const eventLoading  = ref(true); // Loading state
  
    // Fetch the event data
    const event = createResource({
        url: 'e_desk.e_desk.api.frontend_api.GetValue',
        method: 'GET',
        makeParams() {
            return {
                doctype: 'Confer',
                filter: JSON.stringify({ name: route.params.id }), // Serialize the filter object
                field: ['name', 'start_date', 'end_date', 'venuelocation', 'banner_image', 'registration_close_date'],
                dict: true
            }
        },
        auto: true,
        onSuccess() {
            eventLoading.value = false;
        }
    });

    // Only pass data once it's fully loaded
    let eventData = computed(() => {
        if (!eventLoading.value && event.data && typeof event.data === 'object') {
            console.log(event.data,"llllllllllllllllllllllllllllllllllllllllllllllllllll");
            
            return event.data;
        }
        return null; // Return null if data is not yet available
    });
  </script>