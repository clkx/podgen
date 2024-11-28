<template>
  <div class="flex-1 p-6 flex space-x-6">
    <!-- 左側 - 人物設定區域 -->
    <div class="w-1/2 bg-white rounded-lg shadow-md p-6 flex flex-col">
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
    <div class="w-1/2 bg-white rounded-lg shadow-md p-6 flex flex-col">
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
        <h3 class="text-lg font-medium mb-3 text-gray-700">Uploaded PDFs</h3>
        <PDFList 
          :pdfs="uploadedPDFs"
          @view="viewPDF"
          @delete="deletePDF"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileUploader from '@/components/FileUploader.vue'
import PDFList from '@/components/PDFList.vue'

// 主持人設定
const hostName = ref('')
const hostCharacter = ref('')

// 來賓設定
const guestName = ref('')
const guestCharacter = ref('')

// PDF 相關
const uploadedPDFs = ref([
  { name: '頻道簡介v2.pdf' },
  { name: 'AI 趨勢周報_第250期.pdf' },
  { name: '台灣企業 AI 準備度調查報告.pdf' }
])

const saveCharacterSettings = () => {
  // TODO: 實作儲存角色設定的邏輯
  const settings = {
    host: {
      name: hostName.value,
      character: hostCharacter.value
    },
    guest: {
      name: guestName.value,
      character: guestCharacter.value
    }
  }
  console.log('儲存角色設定:', settings)
  // 可以加入提示訊息
  alert('角色設定已儲存！')
}

const handleFilesUploaded = (files) => {
  files.forEach(file => {
    uploadedPDFs.value.push({ name: file.name })
  })
}

const viewPDF = (pdf) => {
  console.log('查看PDF:', pdf.name)
}

const deletePDF = (index) => {
  uploadedPDFs.value.splice(index, 1)
}
</script> 