<template>
  <div class="flex-1 p-6 flex space-x-6">
    <!-- 左側：Azure TTS 設定 -->
    <div class="w-1/2 bg-white rounded-lg shadow-md p-6 flex flex-col">
      <h2 class="text-2xl font-semibold mb-4">Azure TTS 設定</h2>
      <p class="text-gray-600 mb-6">
        選擇主持人和來賓的語音，您可以透過試聽功能來確認語音效果。未來也將支援更多的語音服務。
      </p>

      <!-- 主持人語音設定 -->
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-3">主持人語音</h3>
        <div class="bg-gray-50 p-4 rounded-md border border-gray-200 space-y-4">
          <div class="flex flex-col space-y-2">
            <label class="text-gray-700">選擇語音</label>
            <select 
              v-model="hostVoice" 
              class="border border-gray-300 rounded-md p-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option 
                v-for="voice in azureVoices" 
                :key="voice.id" 
                :value="voice.id"
              >
                {{ voice.name }} ({{ voice.gender }})
              </option>
            </select>
          </div>
          
          <div class="flex items-center justify-between">
            <span class="text-gray-600 text-sm">點擊試聽來預覽語音效果</span>
            <button 
              @click="previewVoice('host')"
              class="bg-[#1e2235] text-white px-4 py-2 rounded-md hover:bg-[#2c3e50] transition-all duration-300 flex items-center"
            >
              試聽 <i class="fas fa-play ml-2"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 來賓語音設定 -->
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-3">來賓語音</h3>
        <div class="bg-gray-50 p-4 rounded-md border border-gray-200 space-y-4">
          <div class="flex flex-col space-y-2">
            <label class="text-gray-700">選擇語音</label>
            <select 
              v-model="guestVoice" 
              class="border border-gray-300 rounded-md p-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option 
                v-for="voice in azureVoices" 
                :key="voice.id" 
                :value="voice.id"
              >
                {{ voice.name }} ({{ voice.gender }})
              </option>
            </select>
          </div>
          
          <div class="flex items-center justify-between">
            <span class="text-gray-600 text-sm">點擊試聽來預覽語音效果</span>
            <button 
              @click="previewVoice('guest')"
              class="bg-[#1e2235] text-white px-4 py-2 rounded-md hover:bg-[#2c3e50] transition-all duration-300 flex items-center"
            >
              試聽 <i class="fas fa-play ml-2"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 儲存按鈕 -->
      <div class="mt-auto">
        <button 
          @click="saveSettings"
          class="w-full bg-gradient-to-r from-[#26c6da] to-[#2196f3] text-white px-6 py-3 rounded-md flex items-center justify-center hover:from-[#2196f3] hover:to-[#26c6da] transition-all duration-300"
        >
          <i class="fas fa-save mr-2"></i> 儲存設定
        </button>
      </div>
    </div>

    <!-- 右側：未來功能預告 -->
    <div class="w-1/2 bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-semibold">即將推出</h2>
        <i class="fas fa-rocket text-gray-400"></i>
      </div>
      
      <div class="bg-blue-50 p-4 rounded-md flex items-center space-x-2 mb-6 border border-blue-100">
        <i class="fas fa-info-circle text-blue-500"></i>
        <span class="text-blue-700">更多語音服務即將推出，敬請期待！</span>
      </div>

      <!-- 未來功能預覽卡片 -->
      <div class="space-y-4">
        <div class="bg-gray-50 p-4 rounded-md flex items-center justify-between border border-gray-200">
          <div class="flex items-center space-x-4">
            <i class="fas fa-microphone text-2xl text-gray-500"></i>
            <div>
              <span class="text-lg font-medium">AI 語音複製</span>
              <p class="text-sm text-gray-500">使用您的聲音來生成 AI 語音</p>
            </div>
          </div>
          <span class="text-blue-500">即將推出</span>
        </div>

        <div class="bg-gray-50 p-4 rounded-md flex items-center justify-between border border-gray-200">
          <div class="flex items-center space-x-4">
            <i class="fas fa-language text-2xl text-gray-500"></i>
            <div>
              <span class="text-lg font-medium">多語言支援</span>
              <p class="text-sm text-gray-500">支援更多語言的語音合成</p>
            </div>
          </div>
          <span class="text-blue-500">即將推出</span>
        </div>

        <div class="bg-gray-50 p-4 rounded-md flex items-center justify-between border border-gray-200">
          <div class="flex items-center space-x-4">
            <i class="fas fa-sliders-h text-2xl text-gray-500"></i>
            <div>
              <span class="text-lg font-medium">進階語音調整</span>
              <p class="text-sm text-gray-500">調整語速、音調等參數</p>
            </div>
          </div>
          <span class="text-blue-500">即將推出</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCharacterStore } from '../stores/character'

const characterStore = useCharacterStore()

// Azure 語音列表
const azureVoices = ref([
  { id: 'zh-TW-HsiaoChenNeural', name: '曉臻', gender: '女性' },
  { id: 'zh-TW-YunJheNeural', name: '雲哲', gender: '男性' },
  { id: 'zh-TW-HsiaoYuNeural', name: '曉雨', gender: '女性' }
])

// 主持人和來賓的語音設定
const hostVoice = ref(characterStore.host.voice.name)
const guestVoice = ref(characterStore.guest.voice.name)

// 試聽語音
const previewVoice = async (role) => {
  const voice = role === 'host' ? hostVoice.value : guestVoice.value
  const text = role === 'host' ? '你好，我是主持人' : '你好，我是來賓'
  
  try {
    const response = await fetch('http://localhost:8000/api/synthesize/preview', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice,
        service: 'azure'
      })
    })

    if (!response.ok) {
      throw new Error('語音預覽失敗')
    }

    const audioBlob = await response.blob()
    const audioUrl = URL.createObjectURL(audioBlob)
    const audio = new Audio(audioUrl)
    audio.play()
  } catch (error) {
    console.error('語音預覽失敗:', error)
    // 這裡可以加入錯誤提示
  }
}

// 儲存設定
const saveSettings = () => {
  console.log('=== 儲存語音設定 ===')
  console.log('主持人語音設定:', hostVoice.value)
  console.log('來賓語音設定:', guestVoice.value)
  
  characterStore.updateVoiceSettings({
    host: {
      name: hostVoice.value
    },
    guest: {
      name: guestVoice.value
    }
  })

  console.log('更新後的 characterStore:', {
    host: characterStore.host,
    guest: characterStore.guest
  })
}

// 載入設定
onMounted(() => {
  console.log('=== 載入語音設定 ===')
  characterStore.loadSettings()
  console.log('載入前的語音設定:', {
    hostVoice: hostVoice.value,
    guestVoice: guestVoice.value
  })
  
  hostVoice.value = characterStore.host.voice.name
  guestVoice.value = characterStore.guest.voice.name
  
  console.log('載入後的語音設定:', {
    hostVoice: hostVoice.value,
    guestVoice: guestVoice.value
  })
})
</script>

<style scoped>
select {
  @apply appearance-none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

/* 深色模式適配 */
@media (prefers-color-scheme: dark) {
  select {
    @apply text-gray-900;
  }
}
</style> 