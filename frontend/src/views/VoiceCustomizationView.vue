<template>
  <div class="flex-1 p-4 md:p-6">
    <div class="bg-white rounded-lg shadow-md p-4 md:p-6">
      <h2 class="text-2xl font-semibold mb-4">語音客製化</h2>
      <p class="text-gray-600 mb-6">在此設定主持人和來賓的語音特徵</p>

      <!-- 主持人語音設定 -->
      <div class="mb-8">
        <div class="flex items-center mb-4">
          <i class="fas fa-microphone text-blue-500 mr-2"></i>
          <h3 class="text-lg font-medium text-gray-700">主持人語音</h3>
        </div>
        <div class="space-y-4 md:space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">語速調整</label>
            <div class="flex items-center space-x-4">
              <input 
                type="range" 
                v-model="hostSpeed" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="w-64"
              >
              <span class="text-gray-600">{{ hostSpeed }}x</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">音調調整</label>
            <div class="flex items-center space-x-4">
              <input 
                type="range" 
                v-model="hostPitch" 
                min="-10" 
                max="10" 
                step="1"
                class="w-64"
              >
              <span class="text-gray-600">{{ hostPitch }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 來賓語音設定 -->
      <div class="mb-8">
        <div class="flex items-center mb-4">
          <i class="fas fa-user text-green-500 mr-2"></i>
          <h3 class="text-lg font-medium text-gray-700">來賓語音</h3>
        </div>
        <div class="space-y-4 md:space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">語速調整</label>
            <div class="flex items-center space-x-4">
              <input 
                type="range" 
                v-model="guestSpeed" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="w-64"
              >
              <span class="text-gray-600">{{ guestSpeed }}x</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-2">音調調整</label>
            <div class="flex items-center space-x-4">
              <input 
                type="range" 
                v-model="guestPitch" 
                min="-10" 
                max="10" 
                step="1"
                class="w-64"
              >
              <span class="text-gray-600">{{ guestPitch }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 試聽區域 -->
      <div class="bg-gray-50 p-4 rounded-lg mb-6">
        <h3 class="text-lg font-medium text-gray-700 mb-4">試聽範例</h3>
        <div class="space-y-4">
          <div class="flex items-center space-x-4">
            <button 
              @click="playHostSample"
              class="bg-blue-100 text-blue-600 px-4 py-2 rounded-md hover:bg-blue-200 transition-colors"
            >
              <i class="fas fa-play mr-2"></i>
              主持人語音範例
            </button>
            <button 
              @click="playGuestSample"
              class="bg-green-100 text-green-600 px-4 py-2 rounded-md hover:bg-green-200 transition-colors"
            >
              <i class="fas fa-play mr-2"></i>
              來賓語音範例
            </button>
          </div>
        </div>
      </div>

      <!-- 儲存按鈕 -->
      <button 
        @click="saveVoiceSettings"
        class="bg-gradient-to-r from-[#26c6da] to-[#2196f3] text-white px-6 py-2 rounded-md hover:from-[#2196f3] hover:to-[#26c6da] transition duration-300 flex items-center justify-center"
      >
        <i class="fa-solid fa-floppy-disk mr-2"></i> 儲存設定
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { localStorageAPI } from '@/services/api'

// 主持人語音設定
const hostSpeed = ref(1.0)
const hostPitch = ref(0)

// 來賓語音設定
const guestSpeed = ref(1.0)
const guestPitch = ref(0)

// 載入初始設定
onMounted(() => {
  const settings = localStorageAPI.getVoiceSettings()
  hostSpeed.value = settings.host.speed
  hostPitch.value = settings.host.pitch
  guestSpeed.value = settings.guest.speed
  guestPitch.value = settings.guest.pitch
})

// 儲存設定
const saveVoiceSettings = async () => {
  try {
    await localStorageAPI.saveVoiceSettings({
      host: {
        speed: hostSpeed.value,
        pitch: hostPitch.value
      },
      guest: {
        speed: guestSpeed.value,
        pitch: guestPitch.value
      }
    })
    alert('設定已儲存！')
  } catch (error) {
    alert('儲存失敗，請稍後再試')
    console.error('儲存失敗:', error)
  }
}

// 試聽功能
const playHostSample = async () => {
  try {
    const response = await audioAPI.getSample('host')
    // TODO: 播放音頻
    console.log('播放音頻:', response.data.data.audio_url)
  } catch (error) {
    console.error('獲取音頻失敗:', error)
  }
}

const playGuestSample = async () => {
  try {
    const response = await audioAPI.getSample('guest')
    // TODO: 播放音頻
    console.log('播放音頻:', response.data.data.audio_url)
  } catch (error) {
    console.error('獲取音頻失敗:', error)
  }
}
</script>

<style scoped>
input[type="range"] {
  -webkit-appearance: none;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #2196f3;
  border-radius: 50%;
  cursor: pointer;
  transition: background .3s ease-in-out;
}

input[type="range"]::-webkit-slider-thumb:hover {
  background: #1976d2;
}

input[type="range"]::-webkit-slider-thumb:active {
  transform: scale(1.1);
}
</style> 