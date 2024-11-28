<template>
  <div class="relative">
    <input
      type="file"
      accept=".pdf"
      class="hidden"
      ref="fileInput"
      @change="handleFileChange"
    >
    <div
      class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer"
      @click="$refs.fileInput.click()"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="{ 'border-blue-500 bg-blue-50': isDragging }"
    >
      <div v-if="selectedFile">
        <i class="fas fa-file-pdf text-2xl text-blue-500 mb-2"></i>
        <p class="text-gray-600">{{ selectedFile.name }}</p>
        <button 
          @click.stop="clearFile" 
          class="mt-2 text-red-500 hover:text-red-600"
        >
          移除檔案
        </button>
      </div>
      <div v-else>
        <i class="fas fa-cloud-upload-alt text-2xl text-gray-400 mb-2"></i>
        <p class="text-gray-500">點擊或拖曳檔案至此處上傳</p>
        <p class="text-sm text-gray-400 mt-1">支援的格式：PDF</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['files-uploaded'])
const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
    emit('files-uploaded', [file])
  } else {
    alert('請上傳 PDF 檔案')
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
    emit('files-uploaded', [file])
  } else {
    alert('請上傳 PDF 檔案')
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('files-uploaded', [])
}

defineExpose({
  clearFile
})
</script> 