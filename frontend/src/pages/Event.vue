<!-- router.push({ name: 'About' }); -->
 <template>
    <Navbar/>
    <Banner event:event/>
 </template>

 <script setup>
  import { ref, computed , inject } from 'vue'
  import { Button, Dialog, createDocumentResource, createResource } from "frappe-ui"
  import Navbar from '../component/Navbar.vue'
  import Banner from '../component/Banner.vue'
  import { useOutletStore } from '../store/eventStore'

  const event = useOutletStore(); 
//   const event=inject("event")
  console.log(event.event,"kkkkkkk");
//   createDocumentResource({
//    doctype: 'ToDo',
//    name: event.event,
//    onSuccess(data) {
//       console.log(data,"iiiiiiiiiiiiiiiiiiiiiii");
      
//    },
//   })


//   doc.get()
//   doc.get
//   console.log(doc.doc,"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@");

  
</script>