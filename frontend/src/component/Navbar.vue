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
                    Sponsers
                </li>
                <li class="hover:overline decoration-4 decoration-red-800">  
                    Venue
                </li>
                <li v-if="session.isLoggedIn" class=" rounded-full flex justify-center items-center">  
                    <img v-if="userData && userData.user_image" :src="userData.user_image" alt="User Image" class="rounded-full  w-7 h-7">
                    <!-- {{userData.user_image}} -->
                </li>
                <li v-else class="hover:overline decoration-4 decoration-red-800">  
                    Login
                </li>
            </ul>
        </div>
    </div>
</template>
<script setup >
 import { computed, ref } from 'vue';
    import { session } from '../data/session';
    import { createResource } from 'frappe-ui';

    const user = createResource({
        url: 'e_desk.e_desk.api.frontend_api.GetValue',
        method: 'GET',
        makeParams() {
            return {
                doctype: 'User',
                filter: JSON.stringify({ name: session.user }), 
                field: ['user_image'],
                dict: true
            }
        },
        auto: true
    });
    let userData = computed(() => {
        if ( user.data && typeof user.data === 'object') {
            return user.data;
        }
        return null; // Return null if data is not yet available
    });
    
</script>