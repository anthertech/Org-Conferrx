<template>
    <div class="border-b-2 w-full  h-[70px] flex justify-around items-center fixed ">
        <div class="w-[70px]"><img src="" alt="Logo" /></div>
        <div class="flex justify-center items-center">
            <ul class="flex   justify-center items-center gap-6 text-sm hover:cursor-pointer">
                <li class="hover:overline decoration-4 decoration-red-800  duration-1000">                    
                    Home
                </li>
                <li class="hover:overline decoration-4 decoration-red-800">  
                    Agenda
                </li>
                <li class="hover:overline decoration-4 decoration-red-800">  
                    Speakers
                </li>
                <li class="hover:overline decoration-4 decoration-red-800">  
                    Sponsors
                </li>
                <li class="hover:overline decoration-4 decoration-red-800">  
                    Venue
                </li>
                <li v-if="session.isLoggedIn" class=" rounded-full flex justify-center items-center" @click="openDialog">  
                    <img v-if="user && user.user_image" :src="user.user_image" alt="User Image" class="rounded-full  w-7 h-7">
                    <p v-else>
                        <div class="rounded-full flex justify-center items-center  w-7 h-7 bg-gray-300">
                            <FeatherIcon name="user" class="  w-5 h-5"/>
                        </div>
                    </p>
                </li>
                <li v-else class="hover:overline decoration-4 decoration-red-800">  
                    Login
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
    import { defineProps ,defineEmits } from 'vue';
    import { session } from '../data/session';
    import { FeatherIcon } from 'frappe-ui';

    const emit = defineEmits(['toggle-dialog']); // Declaring event
    const props = defineProps({
        user: Object,
    
    });
    

    

    const openDialog = () => {
  emit('toggle-dialog'); // Emits the custom event
}
</script>
