<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">背景知識</h1>
    
    <!-- PDF 上傳區域 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="bg-blue-50 p-4 rounded-md flex items-center space-x-2 mb-4">
        <i class="fas fa-info-circle text-blue-500"></i>
        <span class="text-blue-700">現已支援通過上傳PDF檔案來提供背景知識</span>
      </div>
      
      <!-- 使用新的 ReferenceFileUploader 組件 -->
      <ReferenceFileUploader 
        @upload-success="handleUploadSuccess"
      />
    </div>

    <!-- 已上傳的參考資料列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold">已上傳的參考資料</h2>
        <div class="text-sm text-gray-500">
          共 {{ pdfList.length }} 個檔案
        </div>
      </div>

      <!-- 列表為空時的提示 -->
      <div v-if="!pdfList.length" 
           class="text-center py-12 text-gray-500">
        <i class="fas fa-file-pdf text-4xl mb-4 opacity-50"></i>
        <p>尚未上傳任何 PDF 檔案</p>
      </div>

      <!-- PDF 列表 -->
      <TransitionGroup 
        name="list" 
        tag="div" 
        class="space-y-4"
      >
        <div v-for="pdf in pdfList" 
             :key="pdf.folder_name" 
             class="border rounded-lg p-4 flex items-center justify-between hover:shadow-md transition-shadow duration-200">
          <div class="flex items-center space-x-4">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <i class="fas fa-file-pdf text-blue-500"></i>
            </div>
            <div>
              <div class="font-medium">{{ pdf.folder_name }}</div>
              <div class="text-sm text-gray-500 flex items-center space-x-2">
                <i class="fas fa-clock text-xs"></i>
                <span>{{ formatTime(pdf.created_time) }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button @click="viewPDF(pdf.folder_name)" 
                    class="text-blue-500 hover:text-blue-600 p-2 hover:bg-blue-50 rounded-full transition-colors">
              <i class="fas fa-eye"></i>
            </button>
            <button @click="deletePDF(pdf.folder_name)"
                    class="text-red-500 hover:text-red-600 p-2 hover:bg-red-50 rounded-full transition-colors">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ReferenceFileUploader from '@/components/ReferenceFileUploader.vue'
import { pdfAPI } from '@/services/api'

const pdfList = ref([])

// 載入 PDF 列表
const loadPDFList = async () => {
  try {
    const response = await pdfAPI.getPDFList()
    pdfList.value = response.data.references
  } catch (error) {
    console.error('載入 PDF 列表失敗:', error)
  }
}

// 處理上傳成功
const handleUploadSuccess = async () => {
  try {
    // 重新載入列表
    await loadPDFList()
    
    // 強制重新渲染上傳組件
    if (fileUploader.value) {
      fileUploader.value.resetUploader()
    }
  } catch (error) {
    console.error('更新列表失敗:', error)
  }
}

// 格式化時間
const formatTime = (timeString) => {
  const date = new Date(timeString)
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 查看 PDF
const viewPDF = (folderName) => {
  window.open(`http://localhost:8000/api/reference/${folderName}/pdf`, '_blank')
}

// 刪除 PDF
const deletePDF = async (folderName) => {
  if (!confirm('確定要刪除這個 PDF 檔案嗎？')) return
  
  try {
    await pdfAPI.deletePDF(folderName)
    await loadPDFList()
  } catch (error) {
    console.error('刪除失敗:', error)
    alert('刪除失敗，請稍後再試')
  }
}

// 組件掛載時載入 PDF 列表
onMounted(() => {
  loadPDFList()
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 