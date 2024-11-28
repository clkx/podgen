<template>
  <ul class="space-y-2">
    <li 
      v-for="(pdf, index) in pdfs" 
      :key="index" 
      class="flex items-center justify-between bg-gray-50 p-3 rounded-md border border-gray-200"
    >
      <span class="text-gray-700">{{ pdf.name }}</span>
      <div>
        <button 
          @click="$emit('view', pdf)" 
          class="text-blue-500 hover:text-[#22b5c7] mr-2 transition duration-300"
        >
          <i class="fas fa-eye"></i>
        </button>
        <button 
          @click="$emit('delete', index)" 
          class="text-red-500 hover:text-red-700 transition duration-300"
        >
          <i class="fas fa-trash-alt"></i>
        </button>
      </div>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  pdfs: {
    type: Array,
    required: true
  }
})

defineEmits(['view', 'delete'])
</script> 