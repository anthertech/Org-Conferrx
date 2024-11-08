<template>
    <div class="flex flex-col  xl:flex-row justify-between xl:mx-64 mt-36 mb-28">
        <div class="xl:block  flex  items-center flex-col  w-full xl:w-1/2 ">
            <div class="flex flex-col gap-5 ">
                <p class="font-bold" style="font-size:45px;">
                    {{event.name}}
                </p>
                <p class="flex gap-2">
                    <FeatherIcon class="w-5 h-5" name="calendar"/> 
                    {{ formattedDateRange }}
                    <FeatherIcon class="w-5 h-5" name="clock"/> {{ formattedStartTime }}
                </p>
                <p class="flex gap-2">
                    <FeatherIcon class="w-5 h-5" name="map-pin"/> {{event.venuelocation}}
                </p>

                <p v-if="new Date(event.registration_close_date) < new Date()" class="border-2 p-2 w-fit hover:cursor-not-allowed">
    Event has ended
</p>
<p v-else class="border-2 p-2 w-fit hover:cursor-pointer" @click="handleRegisterDialog">
    Register Now
</p>
            </div>
        </div>
        <div class="w-full sm:flex sm:justify-center sm:items-center xl:block  xl:w-1/2">
            <div class="sm:w-3/6 xl:w-full ">
                <img :src="event.banner_image" alt="Conference Image">
            </div>
        </div>
    </div>
    
    <div>
        <img class="" src="/bg.png" alt="Background Image">
    </div>

    <Dialog v-model="dialog2">
        <template #body-title>
            <h3>Register</h3>
        </template>
        <template #body-content>
            <div class="flex flex-col gap-5">
                <div class="flex gap-5">
                    <FormControl
                        :type="'text'"
                        size="sm"
                        variant="subtle"
                        placeholder="First Name"
                        :disabled="false"
                        label="First Name"
                        v-model="formdata.first_name"
                    />
                    <FormControl
                        :type="'text'"
                            size="sm"
                            variant="subtle"
                            placeholder="Last Name"
                            :disabled="false"
                            label="Last Name"
                            v-model="formdata.last_name"
                    />
                </div>
                <div class="flex gap-5">
                    <FormControl
                        :type="'text'"
                        size="sm"
                        variant="subtle"
                        placeholder="Mobile"
                        :disabled="false"
                        label="Mobile Phone"
                        v-model="formdata.mobile"
                    />
                    <FormControl
                        :type="'text'"
                        size="sm"
                        variant="subtle"
                        placeholder="Email"
                        :disabled="false"
                        label="Email"
                        v-model="formdata.email"
                    />

                </div>
                <div class="flex gap-5">
                    <div class="w-1/2">
                        <FormControl
                            type="autocomplete"
                            :options="feilds.Salutation"
                            size="sm"
                            variant="subtle"
                            placeholder="Prefix"
                            :disabled="false"
                            label="Prefix"
                            v-model="formdata.prifix"
                        />
                    </div>
                    <div class="w-1/2">
                        <FormControl
                            type="autocomplete"
                            :options="feilds['Business Category']"
                            size="sm"
                            variant="subtle"
                            placeholder="Business Category"
                            :disabled="false"
                            label="Business Category"
                            v-model="formdata.bussines"
                        />
                    </div>
                </div>
                <div class="flex gap-5">
                    <div class="w-1/2">
                        <FormControl
                            type="autocomplete"
                            :options="feilds.Roles"
                            size="sm"
                            variant="subtle"
                            placeholder="Role"
                            :disabled="false"
                            label="Role"
                            v-model="formdata.role"
                        />
                    </div>
                    <div class="w-1/2">
                        <FormControl
                            type="autocomplete"
                            :options="feilds.Chapter"
                            size="sm"
                            variant="subtle"
                            placeholder="Chapter"
                            :disabled="false"
                            label="Chapter"
                            v-model="formdata.chapter"
                        />
                    </div>
                </div>
                <FileUploader
                    :fileTypes="['image/*']"
                    :validateFile="(fileObject) => {
                    }"
                    @success="(file) => {
                        console.log(file);
                        formdata.image=file
                    }"
                >
                <template #default="{ file, uploading, progress, uploaded, message, error, total, success, openFileSelector }">
                    <Button
                        @click="openFileSelector"
                        :loading="uploading"
                        class="bg-green"
                        
                    >
                    <div class="flex">

                        <p v-if="progress==100">
                            Uploaded 
                        </p>
                        <p v-else-if="progress > 0 && progress < 100">
                            Uploading
                        </p>
                        <p v-else>
                            Upload 
                        </p>
                        
                        <p v-if="progress > 0 && progress < 100">
                            {{ progress }}%
                        </p>
                    </div>
                    </Button>
                </template>
                </FileUploader>
            </div>
        </template>
            <template #actions>
                <div class="w-full flex justify-between">
                    <Button class="ml-2" @click="dialog2 = false">
                        Close
                    </Button>
                    <Button variant="solid" @click="handleCreate">
                        Confirm
                    </Button>
                </div>
            </template>
    </Dialog>

</template>

<script setup>
    import { formatDateRange } from '../utils/dateFormatter';  
    import {useToast} from 'vue-toast-notification';
    import 'vue-toast-notification/dist/theme-sugar.css';
    import { ref , defineProps , computed } from 'vue';
    import { FeatherIcon, Button ,Dialog , FormControl , FileUploader, createResource } from "frappe-ui";
    const  formdata=ref({
        first_name:'',
        last_name:'',
        mobile:'',
        email:'',
        prifix:'',
        bussines:'',
        role:'',
        chapter:'',
        image:'',
    })
    const dialog2 = ref(false);

    const toast = useToast();

    const props = defineProps({
        event: Object,
    
    });
 
    const formattedDateRange = computed(() => {
    return formatDateRange(props.event.start_date, props.event.end_date);
});
const formattedStartTime = computed(() => {
        if (props.event.start_date) {
            let date = new Date(props.event.start_date);
            return date.toLocaleString('en-US', {
                hour: 'numeric',
                minute: 'numeric',
                hour12: true
            });
        }
        return '';
    });

    
    let post = createResource({
        url: 'e_desk.e_desk.api.frontend_api.Getlist', 
        method: 'GET',
        makeParams() {
            return {
                doctype:['Business Category','Salutation','Chapter','Roles']         
            }
        },
        // auto: true,
        onSuccess(data) {
            console.log(data, "Response from server");
            dialog2.value = true;

        },
    });
  
    const handleRegisterDialog = () => {
        post.fetch()
    }
    const handleCreate=()=>{
        formdata.value ['confer']=props.event.name
    
        let sent = createResource({
            url: 'e_desk.e_desk.api.frontend_api.ParticipantCreate', 
            method: 'POST',
            makeParams() {
                return {
                    data:formdata.value        
                }
            },
            onSuccess(data) {
                console.log(data, "Response from server");
                // console.log();

                if (data.status!=200){
                    toast.warning(data.message);
                }else{
                    toast.success(data.message)
                    setTimeout(() => {
                        dialog2.value = false;
                    }, 3000);
                }
                

            },
        });
        sent.fetch()
        }
    let dummuy={
        'Business':{},
        'Category':{},
        'Roles':{},
        'Salutation':{},
        'Chapter':{}
    }
    const feilds = computed(() => {
        if (post.data && typeof post.data === 'object'){
            console.log("Structured list with label and value:", post.data);
            return  post.data
        }
        else{
            return dummuy
        }
    });
</script>
