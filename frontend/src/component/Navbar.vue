<template>
    <div class="border-b-2 w-full  h-[70px] flex lg:justify-around justify-between items-center fixed ">
        <!-- <div class="lg:w-[70px] sm:w-1/2  p-5 lg:p-0 "><img src="" class="" alt="Logo" /></div> -->
        <div class="object-contain h-10 w-20 sm:h-12 sm:w-28 lg:h-14 lg:w-32">  
            <img
            :src="siteLogo"
            alt="Logo"
            class="h-12 object-contain"
            />

        </div>
        <div class="lg:flex hidden justify-center items-center">
            <ul class="flex justify-center items-center gap-6 text-sm hover:cursor-pointer">
                <li
                v-for="item in navbarItems"
                :key="item.label"
                class="hover:overline decoration-4 decoration-red-800"
                @click="goTo(item.url)"
                >
                {{ item.label }}
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
                        label: 'Switch to Desk',
                        icon: () => h(FeatherIcon, { name: 'grid' }),
                        onClick: goToDesk,
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
                            // {
                            //     label: 'Agenda',
                            //     icon: () => h(FeatherIcon, { name: 'calendar' }),
                            // },
                            // {
                            //     label: 'Speakers',
                            //     icon: () => h(FeatherIcon, { name: 'mic' }),
                            // },
                            // {
                            //     label: 'Sponsors',
                            //     icon: () => h(FeatherIcon, { name: 'dollar-sign' }),
                            // },
                            {
                            label: 'Sponsors',
                            icon: () => h(FeatherIcon, { name: 'dollar-sign' }),
                            onClick: () => goToSponsors(),
                        },

                            // {
                            //     label: 'Venue',
                            //     icon: () => h(FeatherIcon, { name: 'map-pin' }),
                            // },
                            session.isLoggedIn
                            ? {
                                label: 'Log out',
                                icon: () => h(FeatherIcon, { name: 'log-out' }),
                                // onClick:logout.fetch(),
                                onClick:handleLogout,
                            }
                            ? {
                                label: 'Switch to Desk',
                                icon: () => h(FeatherIcon, { name: 'grid' }),
                                onClick: goToDesk,
                            }
                            : null

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
import { defineProps, defineEmits, h, ref, onMounted } from 'vue';
import { session } from '../data/session';
import { FeatherIcon, Dropdown, Button, createResource } from 'frappe-ui';
import { useRouter } from 'vue-router';
// import logo from "@/assets/logo_anther_1.png";

const navbarItems = ref([]);
const siteLogo = ref("");

const navbarResource = createResource({
    url: "e_desk.e_desk.api.frontend_api.get_navbar_items",
    method: "GET",
    onSuccess(data) {
        console.log("Navbar API Response:", data);

        if (data?.top_bar_items) {
            navbarItems.value = data.top_bar_items;
        }

        if (data?.logo) {
            siteLogo.value = data.logo;
        }
    }
});


onMounted(() => {
    navbarResource.fetch();
});

const emit = defineEmits(['toggle-dialog']);
const props = defineProps({
    user: Object,
});

const router = useRouter();

const openDialog = () => {
    emit('toggle-dialog');
};

const handleLogout = () => {
    session.logout.fetch()
}

const redirectToLogin = () => {
    window.location.href = "/login?redirect-to=/app";
};

const goToDesk = () => {
    window.location.href = "/app";
};

// dynamic navigation handler
const goTo = (url) => {
    if (!url) return;
    window.location.href = url;
};

const goToSponsors = () => {
    window.location.href = window.location.origin + "/sponsors";
};
</script>
