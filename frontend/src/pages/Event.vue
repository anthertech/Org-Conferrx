<template>
    <div class="h-[75px] ">
        <Navbar @toggle-dialog="dialog2 = true" :user="user" />
    </div>
    <div v-if="eventData">
        <Banner :event="eventData" />
        <Dialog v-model="dialog2">
            <template #body-title>
                <h3>Profile</h3>
            </template>
            <template #body-content>
                <div>
                    <div class="" v-if="participant && !view_qr">
                        <div class="grid  gap-2 sm:grid-cols-2 grid-cols-1">
                            <FormControl
                                :type="'text'"
                                :ref_for="true"
                                size="xl"
                                variant="subtle"
                                placeholder="Placeholder"
                                :disabled="true"
                                label="Name:"
                                v-model="participant.first_name"
                            />
                            <div class="flex justify-center items-end">
                                <Button variant="solid" @click="view_qr = !view_qr ">
                                    <span v-if="view_qr">
                                        Hide Qr
                                    </span>
                                    <span v-else>
                                        View Qr
                                    </span>
                                </Button>
                            </div>
                            <FormControl
                                :type="'text'"
                                :ref_for="true"
                                size="xl"
                                variant="subtle"
                                placeholder="Placeholder"
                                :disabled="true"
                                label="Business Category:"
                                v-model="participant.business_category"
                            />
                            <FormControl
                                :type="'text'"
                                :ref_for="true"
                                size="xl"
                                variant="subtle"
                                placeholder="Placeholder"
                                :disabled="true"
                                label="Chapter:"
                                v-model="participant.chapter"
                            />
                            <FormControl
                                :type="'text'"
                                :ref_for="true"
                                size="xl"
                                variant="subtle"
                                placeholder="Placeholder"
                                :disabled="true"
                                label="Email:"
                                v-model="participant.e_mail"
                            />
                            <FormControl
                                :type="'text'"
                                :ref_for="true"
                                size="xl"
                                variant="subtle"
                                placeholder="Placeholder"
                                :disabled="true"
                                label="Mobile:"
                                v-model="participant.mobile_number"
                            />
                        </div>
                    </div>
                    <div v-else-if=" participant && view_qr" class="w-full h-[200px] flex justify-center">
                        <img :src="participant.qr" alt="">

                    </div>
                    <p v-else>Loading participant data...</p>
                </div>
            </template>
            <template #actions>
                <div class="flex justify-center">
                    <Button variant="solid" v-if="view_qr" @click="view_qr = !view_qr ">
                        <span >
                            Hide Qr
                        </span>
                    </Button>
                </div>      
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { createResource, Dialog , FormControl } from 'frappe-ui';
import Navbar from '../component/Navbar.vue';
import Banner from '../component/Banner.vue';
import { useRoute } from 'vue-router';
import { session } from '../data/session';

const route = useRoute();
const dialog2 = ref(false); // Track dialog state
const eventLoading = ref(true);
const view_qr = ref(false);

// Fetch event data
const event = createResource({
    url: 'e_desk.e_desk.api.frontend_api.GetValue',
    method: 'GET',
    makeParams() {
        return {
            doctype: 'Confer',
            filter: JSON.stringify({ name: route.params.id }),
            field: ['name', 'start_date', 'end_date', 'venuelocation', 'banner_image', 'registration_close_date'],
            dict: true
        };
    },
    auto: true,
    onSuccess() {
        eventLoading.value = false;
    }
});

let eventData = computed(() => {
    if (!eventLoading.value && event.data && typeof event.data === 'object') {
        return event.data;
    }
    return null;
});

// Fetch user data
const userdata = createResource({
    url: 'e_desk.e_desk.api.frontend_api.GetValue',
    method: 'GET',
    makeParams() {
        return {
            doctype: 'User',
            filter: JSON.stringify({ name: session.user }),
            field: ['user_image', 'participant_id'],
            dict: true
        };
    },
    auto: true
});

let user = computed(() => {
    if (userdata.data && typeof userdata.data === 'object') {
        return userdata.data;
    }
    return null;
});

// Participant resource (initialize as null)
const participant = ref(null);

// Watch for `participant_id` and fetch participant data when available
watch(
    () => user.value?.participant_id,
    (participant_id) => {
        if (participant_id) {
            createResource({
                url: 'e_desk.e_desk.api.frontend_api.GetDoc',
                method: 'GET',
                makeParams() {
                    return {
                        doctype: 'Participant',
                        name: participant_id
                    };
                },
                auto: true,
                onSuccess(data) {
                    console.log('Participant data:', data);
                    participant.value = data; // Assign data to the participant
                },
                onError(error) {
                    console.error('Error fetching participant data:', error);
                }
            });
        }
    },
    { immediate: true } // Ensure watcher runs immediately on component mount
);
</script>
