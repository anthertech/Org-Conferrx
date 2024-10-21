<template>
  <Navbar/>
  <Banner event:event/>
</template>

<script setup>
  import {computed } from 'vue'
  import {createResource } from "frappe-ui"
  import Navbar from '../component/Navbar.vue'
  import Banner from '../component/Banner.vue'

  const eventdata  = createResource({
    url: 'e_desk.e_desk.api.frontend_api.default_confer', 
    method: 'GET',
    auto: true,
  });
  
  const event = computed(() => {
    if (eventdata.data && typeof eventdata.data === 'object') {
      return eventdata.data;
    } else {
      return [];
    }
  });
</script>