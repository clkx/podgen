<template>
  <div class="relative">
    <input
      type="file"
      accept=".pdf"
      class="hidden"
      ref="fileInput"
      @change="handleFileChange"
    >
    <!-- 上傳區域 -->
    <div
      class="border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer relative"
      @click="$refs.fileInput.click()"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="{
        'border-blue-500 bg-blue-50': isDragging,
        'border-gray-300 hover:border-blue-500': !isDragging,
        'pointer-events-none': isUploading
      }"
    >
      <!-- 上傳進度顯示 -->
      <div v-if="isUploading" 
           class="absolute inset-0 bg-black bg-opacity-10 flex items-center justify-center rounded-lg">
        <div class="bg-white p-4 rounded-lg shadow-lg text-center">
          <div class="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mb-2 mx-auto"></div>
          <div class="text-sm text-gray-600">正在上傳... {{ progress }}%</div>
        </div>
      </div>

      <!-- 檔案資訊顯示 -->
      <div v-if="selectedFile">
        <i class="fas fa-file-pdf text-2xl text-blue-500 mb-2"></i>
        <p class="text-gray-600">{{ selectedFile.name }}</p>
        <button 
          @click.stop="clearFile" 
          class="mt-2 text-red-500 hover:text-red-600"
          :disabled="isUploading"
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

    <!-- 上傳狀態提示 -->
    <Transition name="fade">
      <div v-if="uploadStatus" 
           :class="{
             'bg-green-100 text-green-700': uploadStatus === 'success',
             'bg-red-100 text-red-700': uploadStatus === 'error'
           }"
           class="mt-2 p-2 rounded-md text-sm text-center">
        {{ statusMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { pdfAPI } from '@/services/api'

const emit = defineEmits(['upload-success'])
const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const progress = ref(0)
const uploadStatus = ref('')
const statusMessage = ref('')

// 處理檔案選擇
const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
    await uploadFile(file)
  } else {
    showStatus('error', '請上傳 PDF 檔案')
  }
}

// 處理檔案拖放
const handleDrop = async (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
    await uploadFile(file)
  } else {
    showStatus('error', '請上傳 PDF 檔案')
  }
}

// 上傳檔案
const uploadFile = async (file) => {
  try {
    isUploading.value = true
    progress.value = 0
    
    const formData = new FormData()
    formData.append('pdf_file', file)
    
    // 模擬上傳進度
    const interval = setInterval(() => {
      progress.value = Math.min(progress.value + 5, 90)
    }, 100)
    
    await pdfAPI.uploadPDF(formData)
    
    clearInterval(interval)
    progress.value = 100
    
    // 顯示成功訊息
    showStatus('success', '上傳成功！')
    
    // 重置上傳器狀態
    resetUploader()
    
    // 通知父組件上傳成功
    emit('upload-success')
    
  } catch (error) {
    console.error('上傳失敗:', error)
    showStatus('error', '上傳失敗，請稍後再試')
  } finally {
    isUploading.value = false
  }
}

// 顯示狀態訊息
const showStatus = (status, message) => {
  uploadStatus.value = status
  statusMessage.value = message
  if (status === 'success') {
    setTimeout(() => {
      uploadStatus.value = ''
      statusMessage.value = ''
    }, 3000)
  }
}

// 清除檔案
const clearFile = () => {
  resetUploader()
}

// 重置上傳器狀態
const resetUploader = () => {
  selectedFile.value = null
  isDragging.value = false
  isUploading.value = false
  progress.value = 0
  uploadStatus.value = ''
  statusMessage.value = ''
  
  // 確保清空檔案輸入
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>