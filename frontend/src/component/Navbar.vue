<template>
    <div class="border-b-2 w-full  h-[70px] flex lg:justify-around justify-between items-center fixed ">
        <div class="lg:w-[70px] sm:w-1/2  p-5 lg:p-0 "><img src="" class="" alt="Logo" /></div>
        <div class="lg:flex hidden justify-center items-center">
            <ul class="flex justify-center items-center gap-6 text-sm hover:cursor-pointer">
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
                <li v-if="session.isLoggedIn" class="rounded-full flex justify-center items-center" >  
                    <Dropdown
                        :options="[
                        {
                        label: 'Profile',
                        onClick: openDialog,
                        icon: () => h(FeatherIcon, { name: 'user' }),
                        },
                        {
                            label: 'Log out',
                            icon: () => h(FeatherIcon, { name: 'log-out' }),
                            // onClick:logout.fetch(),
                            onClick:handleLogout,
                        }
                        ]"
                        >
                        <Button>
                            <template #icon>
                                <img v-if="user && user.user_image" :src="user.user_image" alt="User Image" class="rounded-full w-7 h-7">
                                <div v-else>
                                    <div class="rounded-full flex justify-center items-center w-7 h-7 bg-gray-300">
                                        <FeatherIcon
                                            name="more-horizontal"
                                            class="h-4 w-4"
                                        />
                                    </div>
                                </div>
                            </template>
                        </Button>
                    </Dropdown>
                </li>
                <li v-else class="hover:overline decoration-4 decoration-red-800" @click="redirectToLogin">  
                    Login
                </li>
            </ul>
        </div>
        <div class="lg:hidden w-[20px] mr-10">
            <Dropdown
                :options="[
                    {
                        group: 'Menu',
                        items: [
                            {
                                label: 'Home',
                                icon: () => h(FeatherIcon, { name: 'home' }),
                            },
                            {
                                label: 'Agenda',
                                icon: () => h(FeatherIcon, { name: 'calendar' }),
                            },
                            {
                                label: 'Speakers',
                                icon: () => h(FeatherIcon, { name: 'mic' }),
                            },
                            {
                                label: 'Sponsors',
                                icon: () => h(FeatherIcon, { name: 'dollar-sign' }),
                            },
                            {
                                label: 'Venue',
                                icon: () => h(FeatherIcon, { name: 'map-pin' }),
                            },
                            session.isLoggedIn
                            ? {
                                label: 'Log out',
                                icon: () => h(FeatherIcon, { name: 'log-out' }),
                                // onClick:logout.fetch(),
                                onClick:handleLogout,
                            }
                            : {
                                label: 'Log in',
                                icon: () => h(FeatherIcon, { name: 'log-in' }),
                                onClick: redirectToLogin, 
                            },
                        ],
                    },
                ]"
                class="mr-10"
            >
                <Button>
                    <template #icon>
                        <FeatherIcon
                            name="menu"
                            class="h-5 w-5"
                        />
                    </template>
                </Button>
            </Dropdown>
        </div>
    </div>
</template>

<script setup>
import { defineProps, defineEmits, h } from 'vue';
import { session  } from '../data/session';
import { FeatherIcon, Dropdown, Button, createResource} from 'frappe-ui';
import { useRouter } from 'vue-router'; // Import the useRouter hook

const emit = defineEmits(['toggle-dialog']); // Declaring event
const props = defineProps({
    user: Object,
});

const router = useRouter(); // Initialize router

const openDialog = () => {
    emit('toggle-dialog'); // Emits the custom event
};

const handleLogout = () => {
    session.logout.fetch()
}

const redirectToLogin = () => {
    
    const redirectTo = encodeURIComponent('/home');
    window.location.href =`/login?redirect-to=${redirectTo}#login`; // Redirect to the login page
};
</script>