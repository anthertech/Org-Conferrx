<template>
    <div class="flex justify-between mx-64 mt-36 mb-28">
        <div class="flex flex-col gap-3 w-1/2 ">
            <p class="font-bold" style="font-size:45px;">
                BNI India National Conference 2024
            </p>
            <p class="flex gap-2">
                <FeatherIcon class="w-5 h-5" name="calendar"/> Jun 21 – 23, 2024  
                <FeatherIcon class="w-5 h-5" name="clock"/> 08:00 AM
            </p>
            <p class="flex gap-2">
                <FeatherIcon class="w-5 h-5" name="map-pin"/> Mumbai, Maharashtra - India
            </p>
            <p class="border-2 p-2 w-fit" @click="handleRegisterDialog">
                Event has ended
            </p>
        </div>
        <div class="w-1/2">
            <img src="https://previewengine-accl.zohopublic.in/image/BACKSTAGE/18033000000113044?cli-msg=eyJtb2R1bGUiOiJFdmVudEltYWdlUmVzb3VyY2UiLCJ0eXBlIjowLCJwb3J0YWxJZCI6IjYwMDI4OTQ1ODE3Iiwic3ViUmVzb3VyY2VJZCI6IjYwMDI4OTQ1ODE3IiwiaWQiOiIxODAzMzAwMDAwMDExMzA0NCJ9" alt="Conference Image">
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
                    placeholder="Placeholder"
                    :disabled="false"
                    label="First Name"
                    v-model="formdata.first_name"
                    />
                <FormControl
                :type="'text'"
                    size="sm"
                    variant="subtle"
                    placeholder="Placeholder"
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
                    placeholder="Placeholder"
                    :disabled="false"
                    label="Mobile Phone"
                    v-model="formdata.mobile"
                    />
                    <FormControl
                    :type="'text'"
                    size="sm"
                    variant="subtle"
                    placeholder="Placeholder"
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
                    placeholder="Placeholder"
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
                    placeholder="Placeholder"
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
                    placeholder="Placeholder"
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
                    placeholder="Placeholder"
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
                    //  handlefile(file);
                    console.log(file);
                    formdata.image=file

                }"
                >
                <template #default="{ file, uploading, progress, uploaded, message, error, total, success, openFileSelector }">
                    <Button
                        @click="openFileSelector"
                        :loading="uploading"
                    >
                        Uploading {{ progress }}%
                    </Button>
                </template>
            </FileUploader>
            
            
        </div>
        </template>
        <template #actions>
            <Button variant="solid" @click="handleCreate">
                Confirm
            </Button>
            <Button class="ml-2" @click="dialog2 = false">
                Close
            </Button>
        </template>
    </Dialog>
</template>

<script setup>

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


    const props = defineProps({
        event: Object,
    
    });
 

    let post = createResource({
        url: 'e_desk.e_desk.api.frontend_api.Getdoc', 
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
        console.log(formdata,"ppppppppppppppppppppppp");
    
        let sent = createResource({
            url: 'e_desk.e_desk.api.frontend_api.ParticipantCreate', 
            method: 'POST',
            makeParams() {
                return {
                    data:formdata.value        
                }
            },
            // auto: true,
            onSuccess(data) {
                console.log(data, "Response from server");
                dialog2.value = false;

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
