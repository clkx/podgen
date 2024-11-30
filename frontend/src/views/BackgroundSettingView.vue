<template>
  <div class="flex-1 p-4 md:p-6">
    <div class="flex flex-col md:flex-row md:space-x-6 space-y-6 md:space-y-0">
      <!-- 左側 - 人物設定區域 -->
      <div class="w-full md:w-1/2 bg-white rounded-lg shadow-md p-4 md:p-6">
        <h2 class="text-2xl font-semibold mb-4 text-gray-800">人物設定</h2>
        <p class="text-gray-600 mb-4">
          在此設定您Podcast中的角色身份，讓AI能根據這些特徵生成更加個性化的對話內容
        </p>

        <!-- 主持人設定 -->
        <div class="mb-6">
          <div class="flex items-center mb-4">
            <i class="fas fa-microphone text-blue-500 mr-2"></i>
            <h3 class="text-lg font-medium text-gray-700">主持人設定</h3>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">主持人名稱</label>
              <input 
                v-model="hostName" 
                type="text"
                class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#26c6da]"
                placeholder="請輸入主持人名稱"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">人物設定</label>
              <textarea 
                v-model="hostCharacter" 
                class="w-full p-2 border border-gray-300 rounded-md resize-none h-32 focus:outline-none focus:ring-2 focus:ring-[#26c6da]" 
                placeholder="例如：熱愛科技的Podcast主持人，擁有十年以上的科技行業經驗，語氣風格專業但輕鬆幽默，喜歡以簡單易懂的方式解釋複雜的技術概念"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 來賓設定 -->
        <div class="mb-6">
          <div class="flex items-center mb-4">
            <i class="fas fa-user text-green-500 mr-2"></i>
            <h3 class="text-lg font-medium text-gray-700">來賓設定</h3>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">來賓名稱</label>
              <input 
                v-model="guestName" 
                type="text"
                class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#26c6da]"
                placeholder="請輸入來賓名稱"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">人物設定</label>
              <textarea 
                v-model="guestCharacter" 
                class="w-full p-2 border border-gray-300 rounded-md resize-none h-32 focus:outline-none focus:ring-2 focus:ring-[#26c6da]" 
                placeholder="例如：資深AI研究員，在機器學習領域有豐富經驗，擅長用生活化的例子說明複雜的AI概念，說話風格溫和且富有洞察力"
              ></textarea>
            </div>
          </div>
        </div>

        <button 
          @click="saveCharacterSettings" 
          class="mt-auto bg-gradient-to-r from-[#26c6da] to-[#2196f3] text-white px-6 py-2 rounded-md hover:from-[#2196f3] hover:to-[#26c6da] transition duration-300 flex items-center justify-center"
        >
          <i class="fa-solid fa-floppy-disk mr-2"></i> 儲存設定
        </button>
      </div>

      <!-- 右側 - PDF管理區域 -->
      <div class="w-full md:w-1/2 bg-white rounded-lg shadow-md p-4 md:p-6">
        <h2 class="text-2xl font-semibold mb-4 text-gray-800">背景知識</h2>
        <div class="bg-blue-50 p-4 rounded-md flex items-center space-x-2 mb-4">
          <i class="fas fa-info-circle text-blue-500"></i>
          <span class="text-blue-700">現已支援通過上傳PDF檔案來提供背景知識</span>
          <span class="bg-red-500 text-white text-xs px-2 py-1 rounded">New</span>
        </div>

        <FileUploader 
          @files-uploaded="handleFilesUploaded"
          class="mb-6"
        />

        <div class="flex-1 overflow-y-auto">
          <h3 class="text-lg font-medium mb-3 text-gray-700">已上傳的參考資料</h3>
          <div class="space-y-4">
            <div v-for="(pdf, index) in uploadedPDFs" :key="pdf.name" 
                 class="bg-white p-4 rounded-lg shadow border border-gray-200">
              <div class="flex justify-between items-center">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-800">{{ pdf.name }}</h4>
                  <p class="text-sm text-gray-500">上傳時間：{{ pdf.created_time }}</p>
                </div>
                <div class="flex space-x-2">
                  <button @click="viewPDF(pdf)" 
                          class="text-blue-600 hover:text-blue-800">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button @click="deletePDF(index)" 
                          class="text-red-600 hover:text-red-800">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- PDF 預覽 Modal -->
  <div v-if="showPDFModal" 
       class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg w-[90vw] h-[90vh] flex flex-col">
      <!-- Modal 標題列 -->
      <div class="flex justify-between items-center p-4 border-b">
        <h3 class="text-lg font-medium">PDF 預覽</h3>
        <button @click="closePDFModal" class="text-gray-500 hover:text-gray-700">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- PDF 內容 -->
      <div class="flex-1 p-4">
        <iframe
          v-if="currentPDFUrl"
          :src="currentPDFUrl"
          class="w-full h-full border-0"
          type="application/pdf"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCharacterStore } from '@/stores/character'
import FileUploader from '@/components/FileUploader.vue'
import PDFList from '@/components/PDFList.vue'
import axios from 'axios'

const characterStore = useCharacterStore()

// 主持人設定
const hostName = ref('')
const hostCharacter = ref('')

// 來賓設定
const guestName = ref('')
const guestCharacter = ref('')

// PDF 相關
const uploadedPDFs = ref([])

// 新增 PDF 預覽相關的狀態
const showPDFModal = ref(false)
const currentPDFUrl = ref('')

// 載入初始設定
onMounted(async () => {
  characterStore.loadSettings()
  hostName.value = characterStore.host.name
  hostCharacter.value = characterStore.host.character
  guestName.value = characterStore.guest.name
  guestCharacter.value = characterStore.guest.character
  
  // 載入已上傳的 PDF 列表
  await loadPDFList()
})

// 儲存設定
const saveCharacterSettings = () => {
  characterStore.updateSettings({
    host: {
      name: hostName.value,
      character: hostCharacter.value
    },
    guest: {
      name: guestName.value,
      character: guestCharacter.value
    }
  })
  alert('角色設定已儲存！')
}

// PDF 相關
const loadPDFList = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/references')
    if (response.data.status === 'success') {
      uploadedPDFs.value = response.data.references.map(ref => ({
        name: ref.folder_name,
        files: ref.files,
        created_time: ref.created_time
      }))
    }
  } catch (error) {
    console.error('載入 PDF 列表失敗:', error)
  }
}

const handleFilesUploaded = async (files) => {
  try {
    for (const file of files) {
      const formData = new FormData()
      formData.append('pdf_file', file)
      formData.append('is_temporary', 'false')  // 這是永久儲存
      
      const response = await axios.post('http://localhost:8000/api/upload/pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.status === 'success') {
        // 重新載入 PDF 列表
        await loadPDFList()
      }
    }
  } catch (error) {
    alert('上傳失敗，請稍後再試')
    console.error('上傳失敗:', error)
  }
}

const deletePDF = async (index) => {
  const pdf = uploadedPDFs.value[index]
  try {
    const response = await axios.delete(`http://localhost:8000/api/reference/${pdf.name}`)
    if (response.data.status === 'success') {
      uploadedPDFs.value.splice(index, 1)
    }
  } catch (error) {
    alert('刪除失敗，請稍後再試')
    console.error('刪除失敗:', error)
  }
}

const viewPDF = (pdf) => {
  currentPDFUrl.value = `http://localhost:8000/api/reference/${pdf.name}/pdf`
  showPDFModal.value = true
}

// 關閉 Modal
const closePDFModal = () => {
  showPDFModal.value = false
  currentPDFUrl.value = ''
}
</script>

<style scoped>
/* 防止背景滾動 */
:root {
  overflow: hidden;
}

/* Modal 動畫 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style> 