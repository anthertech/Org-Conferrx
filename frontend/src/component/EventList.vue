<template>
    <div class="flex justify-between">
      <p>{{ event?.name }}</p>
      <p>{{ event?.start_date }}</p>
      <p>{{ event?.end_date }}</p>
      <Button
  :variant="'outline'"
  theme="gray"
  size="sm"
  label="Button"
  :loading="false"
  :loadingText="null"
  :disabled="false"
  :link="null"
  @click="handleevent"
>
  Button
</Button>
    </div>
  </template>
  
  <script setup>

  import { defineProps  } from 'vue';
  import {Button} from 'frappe-ui';
  import { useRouter } from 'vue-router';
  import { useOutletStore } from '../store/eventStore'

  const eventStore = useOutletStore(); 
  // Define props for the component
  const router = useRouter();
  const props = defineProps({
    event: Object,
  });
const handleevent=()=>{
    eventStore.setOutlet(props.event.name);
    console.log("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
    router.push({ name: 'Event' });
}
  </script>