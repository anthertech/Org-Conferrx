<template>
    <div class="w-full h-full">
        <!-- <Navbar/>
        <Banner/> -->
        <div class="  p-32">

            <div class=" bg-red-300 rounded p-5">
                <EventList v-for="event in eventdata" :event="event" :key="event" />
            </div>
        </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed , inject } from 'vue'
  import { Button, Dialog, createResource, ListView } from "frappe-ui"
  import Navbar from '../component/Navbar.vue'
  import Banner from '../component/Banner.vue'
  import EventList from '../component/EventList.vue'
  
  // Fetch data from the backend
  let event = createResource({
    url: 'e_desk.e_desk.api.frontend_api.latest_confer', 
    method: 'GET',
    onSuccess(data) {
      console.log(data);
    },
    auto: true,
  });
  
  const eventdata = computed(() => {
    if (event.data && typeof event.data === 'object') {
      console.log("Structured list with label and value:", event.data);
      return event.data;
    } else {
      return [];
    }
  });
  </script>