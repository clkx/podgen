<template>
  <div class="flex-1 p-6 flex space-x-6">
    <!-- 左側 - 輸入區域 -->
    <div class="w-1/2 bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-semibold">Podcast生成</h2>
      </div>
      <p class="text-gray-600 mb-4">
        輸入您想要討論的主題或想法，由AI自動生成對話腳本與語音，幫助您快速製作出專屬的Podcast內容
      </p>

      <!-- 生成方式選擇 -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-600 mb-2">選擇生成方式</label>
        <div class="grid grid-cols-3 gap-3">
          <button
            @click="selectGenerationType('prompt')"
            class="p-3 border rounded-lg text-center transition-all duration-300"
            :class="generationType === 'prompt' ? 
              'border-blue-500 bg-blue-50 text-blue-700' : 
              'border-gray-300 hover:bg-gray-50 text-gray-700'"
          >
            <i class="fas fa-keyboard mb-2 text-xl"></i>
            <div class="text-sm font-medium">Prompt</div>
            <div class="text-xs text-gray-500 mt-1">自由輸入提示詞</div>
          </button>
          <button
            @click="selectGenerationType('pdf')"
            class="p-3 border rounded-lg text-center transition-all duration-300"
            :class="generationType === 'pdf' ? 
              'border-blue-500 bg-blue-50 text-blue-700' : 
              'border-gray-300 hover:bg-gray-50 text-gray-700'"
          >
            <i class="fas fa-file-pdf mb-2 text-xl"></i>
            <div class="text-sm font-medium">PDF</div>
            <div class="text-xs text-gray-500 mt-1">上傳 PDF 生成</div>
          </button>
          <button
            @click="selectGenerationType('arxiv')"
            class="p-3 border rounded-lg text-center transition-all duration-300"
            :class="generationType === 'arxiv' ? 
              'border-blue-500 bg-blue-50 text-blue-700' : 
              'border-gray-300 hover:bg-gray-50 text-gray-700'"
          >
            <i class="fas fa-graduation-cap mb-2 text-xl"></i>
            <div class="text-sm font-medium">arXiv</div>
            <div class="text-xs text-gray-500 mt-1">學術論文轉換</div>
          </button>
        </div>
      </div>
      
      <!-- 輸入區域 -->
      <div class="mb-4">
        <div v-if="generationType === 'prompt'" class="space-y-4">
          <div class="bg-blue-50 p-4 rounded-md flex items-center space-x-2">
            <i class="fas fa-info-circle text-blue-500"></i>
            <span class="text-blue-700">請盡量提供具體且清晰的提詞</span>
          </div>
          <input 
            v-model="topic"
            type="text" 
            placeholder="生成式AI" 
            class="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-[#26c6da]"
            :disabled="isGenerating"
            @keyup.enter="generatePodcast"
          >
        </div>

        <div v-if="generationType === 'pdf'" class="space-y-4">
          <div class="bg-blue-50 p-4 rounded-md flex items-center space-x-2">
            <i class="fas fa-info-circle text-blue-500"></i>
            <span class="text-blue-700">請上傳想要討論的 PDF 文件</span>
          </div>
          <FileUploader 
            @files-uploaded="handlePDFUpload"
            ref="fileUploader"
          />
        </div>

        <div v-if="generationType === 'arxiv'" class="space-y-4">
          <div class="bg-blue-50 p-4 rounded-md flex items-center space-x-2">
            <i class="fas fa-info-circle text-blue-500"></i>
            <span class="text-blue-700">請輸入 arXiv URL (僅支援有開放 HTML 版本論文)</span>
          </div>
          <input 
            v-model="arxivId"
            type="text" 
            placeholder="例如：https://arxiv.org/abs/1706.03762" 
            class="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-[#26c6da]"
            :disabled="isGenerating"
            @keyup.enter="generatePodcast"
          >
        </div>
      </div>

      <!-- 功能按鈕 -->
      <div class="flex space-x-2">
        <router-link 
          to="/background-setting"
          class="flex-1 border border-gray-300 rounded-md py-2 px-4 flex items-center justify-center hover:bg-gray-50"
          :class="{ 'pointer-events-none opacity-50': isGenerating }"
        >
          <i class="fas fa-cog mr-2"></i> 背景設定
        </router-link>
        <router-link 
          to="/voice-customization"
          class="flex-1 border border-gray-300 rounded-md py-2 px-4 flex items-center justify-center hover:bg-gray-50"
          :class="{ 'pointer-events-none opacity-50': isGenerating }"
        >
          <i class="fas fa-solid fa-globe mr-2"></i>客製語音
        </router-link>
        <button 
          @click="generatePodcast"
          class="bg-[#1e2235] text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isGenerating || !canGenerate"
        >
          <i class="fas" :class="isGenerating ? 'fa-spinner fa-spin' : 'fa-chevron-right'"></i>
        </button>
      </div>
    </div>

    <!-- 右側 - 預覽區域 -->
    <div class="w-1/2 bg-white rounded-lg shadow-md p-6 flex flex-col">
      <!-- 進度顯示區域 -->
      <Transition name="fade-height">
        <div v-if="showProgress" 
             class="progress-area mb-4"
             :class="{ 'fade-out': fadeOutProgress }">
          <!-- 簡約進度顯示 -->
          <div class="flex items-center space-x-4">
            <!-- 當前階段圖標 -->
            <div class="relative">
              <i class="fas text-lg"
                 :class="{
                   'fa-file-alt text-blue-500': generationStatus === 'generating-script',
                   'fa-microphone text-green-500': generationStatus === 'generating-audio'
                 }"></i>
              <div class="absolute -top-1 -right-1 w-2 h-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                      :class="{
                        'bg-blue-400': generationStatus === 'generating-script',
                        'bg-green-400': generationStatus === 'generating-audio'
                      }"></span>
              </div>
            </div>

            <!-- 進度文字 -->
            <div class="flex-1">
              <div class="flex items-center space-x-2 text-sm">
                <!-- 主要狀態文字 -->
                <span class="font-medium">
                  ⚡ 生成中...
                </span>
                <!-- 詳細進度文字 -->
                <span class="text-gray-500">
                  {{ progress.message }}
                </span>
              </div>
            </div>

            <!-- 進度百分比 -->
            <div class="text-sm font-bold"
                 :class="{
                   'text-blue-500': generationStatus === 'generating-script',
                   'text-green-500': generationStatus === 'generating-audio'
                 }">
              {{ Math.round(progress.percentage) }}%
            </div>
          </div>
        </div>
      </Transition>

      <!-- 空白狀態 -->
      <div v-if="!segments.length && !isGenerating" 
           class="flex-1 flex items-center justify-center min-h-[400px]">
        <div class="text-center text-gray-500">
          <i class="fas fa-podcast text-4xl mb-4"></i>
          <p>選擇生成方式並點擊開始生成</p>
        </div>
      </div>

      <!-- 生成腳本時的載入動畫 -->
      <div v-else-if="generationStatus === 'generating-script'"
           class="flex-1 flex items-center justify-center min-h-[400px]">
        <div class="text-center">
          <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mb-4 mx-auto"></div>
          <p class="text-gray-600">{{ progress.message || '正在生成對話腳本...' }}</p>
        </div>
      </div>

      <!-- 對話內容顯示 -->
      <div v-else class="scrollable-content flex-1 mb-4 px-4" ref="chatContainer">
        <TransitionGroup name="fade">
          <div v-for="(segment, index) in segments" 
               :key="index"
               :ref="el => { if (index === currentAudioIndex) currentSegmentRef = el }"
               class="mb-4">
            <!-- 主持人對話 -->
            <div v-if="script?.dialogue[index]?.speaker === script?.host_name" 
                 class="flex items-start transition-all duration-300"
                 :class="{
                   'playing-segment': isPlaying && index === currentAudioIndex,
                   'opacity-50': generationStatus === 'generating-audio' && index > currentProgress?.index
                 }">
              <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-microphone text-blue-500"></i>
              </div>
              <div class="ml-4 flex-1">
                <div class="text-sm text-blue-600 mb-1 flex items-center">
                  <span>{{ script?.host_name }}</span>
                  <span v-if="hasAudio(index)" class="ml-2 text-xs text-green-500">
                    <i class="fas fa-volume-up"></i>
                  </span>
                  <span v-else-if="isCurrentSegment(index)" class="ml-2 text-xs text-blue-500">
                    <i class="fas fa-spinner fa-spin"></i>
                  </span>
                </div>
                <div class="bg-blue-50 rounded-lg p-4 text-gray-700">
                  {{ segment }}
                </div>
              </div>
            </div>

            <!-- 來賓對話 -->
            <div v-else 
                 class="flex items-start justify-end transition-all duration-300"
                 :class="{
                   'playing-segment': isPlaying && index === currentAudioIndex,
                   'opacity-50': generationStatus === 'generating-audio' && index > currentProgress?.index
                 }">
              <div class="mr-4 flex-1">
                <div class="text-sm text-green-600 mb-1 text-right flex items-center justify-end">
                  <span>{{ script?.guest_name }}</span>
                  <span v-if="hasAudio(index)" class="ml-2 text-xs text-green-500">
                    <i class="fas fa-volume-up"></i>
                  </span>
                  <span v-else-if="isCurrentSegment(index)" class="ml-2 text-xs text-blue-500">
                    <i class="fas fa-spinner fa-spin"></i>
                  </span>
                </div>
                <div class="bg-green-50 rounded-lg p-4 text-gray-700">
                  {{ segment }}
                </div>
              </div>
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-user text-green-500"></i>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <!-- 音頻放器 -->
      <div v-if="audioQueue.length > 0" class="bg-[#1e2235] rounded-lg p-4">
        <!-- 進度條容器 -->
        <div class="player-progress-container mb-4 relative cursor-pointer" 
             @click="seekTo($event)"
             @mousemove="updateSeekPreview($event)"
             @mouseleave="hideSeekPreview">
          
          <!-- 背景進度條 -->
          <div class="player-progress-bg"></div>
          
          <!-- 已播放進度 -->
          <div class="player-progress-bar"
               :style="{ width: `${(currentAudioIndex / (audioQueue.length - 1)) * 100}%` }">
            <!-- 進度條把手 -->
            <div class="player-progress-handle"></div>
          </div>
          
          <!-- 預覽指示器 -->
          <div v-if="seekPreview.show" 
               class="player-preview-indicator"
               :style="{ left: `${seekPreview.position}%` }">
            <!-- 預覽標記線 -->
            <div class="preview-line"></div>
            <!-- 預覽氣泡 -->
            <div class="preview-bubble">
              {{ Math.ceil((seekPreview.position / 100) * audioQueue.length) }} / {{ audioQueue.length }}
            </div>
          </div>
        </div>

        <!-- 播放控制區 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4 text-white">
            <!-- 播放/暫停按鈕 -->
            <button @click="podcastStore.togglePlay" 
                    class="play-button">
              <i class="fas" :class="isPlaying ? 'fa-pause' : 'fa-play'"></i>
            </button>
          </div>

          <!-- 進度顯示 -->
          <div class="text-white text-sm font-medium">
            {{ currentAudioIndex + 1 }} / {{ audioQueue.length }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import FileUploader from '@/components/FileUploader.vue'
import { podcastAPI } from '@/services/api'
import { useCharacterStore } from '@/stores/character'
import { usePodcastStore } from '@/stores/podcast'
import { storeToRefs } from 'pinia'

const podcastStore = usePodcastStore()
const characterStore = useCharacterStore()

// 從 store 中解構需要的狀態
const { 
  isGenerating, 
  progress,
  currentProgress, 
  audioQueue, 
  script, 
  isPlaying,
  currentAudioIndex,
  togglePlay,
  showProgress,
  fadeOutProgress
} = storeToRefs(podcastStore)

// 基本狀態
const topic = ref('')
const segments = ref([])
const uploadedPDF = ref(null)

// 功能開關狀態
const useBackgroundKnowledge = ref(false)
const useCharacterSetting = ref(false)
const useVoiceCustomization = ref(false)

// 生成類型相關
const generationType = ref('prompt')
const arxivId = ref('')

// 計算是否可以生成
const canGenerate = computed(() => {
  switch (generationType.value) {
    case 'prompt':
      return topic.value.trim() !== ''
    case 'pdf':
      return uploadedPDF.value !== null
    case 'arxiv':
      return arxivId.value.trim() !== ''
    default:
      return false
  }
})

// 處理 PDF 上傳
const handlePDFUpload = (files) => {
  console.log('收到檔案:', files)  // 添加日誌
  if (files && files.length > 0) {
    uploadedPDF.value = files[0]
  } else {
    uploadedPDF.value = null
  }
}

// 檢查某個段落是否已有語音
const hasAudio = (index) => {
  return audioQueue.value.some(segment => segment.index === index)
}

// 監聽 audioQueue 變，更新對話內容
watch(audioQueue, (newQueue) => {
  console.log('音頻佇列更新:', newQueue)
  // 更新已有語音的段落
  if (newQueue.length > 0) {
    segments.value = script.value.dialogue.map(d => d.content)
  }
}, { deep: true })

// 選擇生成類型
const selectGenerationType = (type) => {
  generationType.value = type
  // 重置相關數據
  topic.value = ''
  arxivId.value = ''
  uploadedPDF.value = null
}

// 生成 Podcast
const generatePodcast = async () => {
  if (!canGenerate.value) return
  
  try {
    // 根據不同生成類型調用不同的 API
    switch (generationType.value) {
      case 'prompt':
        await generateFromPrompt()
        break
      case 'pdf':
        await generateFromPDF()
        break
      case 'arxiv':
        await generateFromArxiv()
        break
    }
  } catch (error) {
    console.error('生成失敗:', error)
  }
}

const generateFromPrompt = async () => {
  if (!topic.value.trim()) {
    alert('請輸入主題')
    return
  }

  try {
    // 清空之前的對話內容
    segments.value = []
    
    // 開始生成
    await podcastStore.generateFromPrompt(topic.value)
    
    // 生成成功後，更新對話內容
    if (audioQueue.value.length > 0) {
      console.log('生成完成，音頻段落數:', audioQueue.value.length)
      segments.value = audioQueue.value.map(segment => segment.content)
    } else {
      console.log('生成完成，但沒有音頻段落')
    }
  } catch (err) {
    console.error('生成失敗:', err)
    alert(err.message || 'Prompt 生成失敗，請稍後再試')
  }
}

const generateFromPDF = async () => {
  if (!uploadedPDF.value) {
    alert('請先上傳 PDF 檔案')
    return
  }

  try {
    // 清空之前的對話內容
    segments.value = []
    
    // 開始生成
    await podcastStore.generateFromPDF(uploadedPDF.value)
    
    // 生成成功後，更新對話內容
    if (audioQueue.value.length > 0) {
      console.log('生成完成，音頻段落數:', audioQueue.value.length)
      segments.value = audioQueue.value.map(segment => segment.content)
    } else {
      console.log('生成完成，但沒有音頻段落')
    }
  } catch (err) {
    console.error('生成失敗:', err)
    alert(err.message || 'PDF 生成失敗，請稍後再試')
  }
}

const generateFromArxiv = async () => {
  if (!arxivId.value) {
    alert('請輸入 arXiv URL')
    return
  }

  try {
    // 清空之前的對話內容
    segments.value = []
    
    // 開始生成
    await podcastStore.generateFromArxiv(arxivId.value)
    
    // 生成成功後，更新對話內容
    if (audioQueue.value.length > 0) {
      console.log('生成完成，音頻段落數:', audioQueue.value.length)
      segments.value = audioQueue.value.map(segment => segment.content)
    } else {
      console.log('生成完成，但沒有音頻段落')
    }
  } catch (err) {
    console.error('生成失敗:', err)
    alert(err.message || 'arXiv 生成失敗，請稍後再試')
  }
}

// 修改模板中的條件判斷
const isCurrentSegment = (index) => {
  return currentProgress.value?.index === index
}

// 添加新的 refs
const chatContainer = ref(null)
const currentSegmentRef = ref(null)

// 監聽當前播放段落的變化
watch([currentAudioIndex, isPlaying], ([newIndex, playing]) => {
  if (playing && currentSegmentRef.value && chatContainer.value) {
    currentSegmentRef.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
})

// 添加進度條相關狀態
const seekPreview = ref({
  show: false,
  position: 0
})

// 更新預覽位置
const updateSeekPreview = (event) => {
  const rect = event.target.getBoundingClientRect()
  const position = ((event.clientX - rect.left) / rect.width) * 100
  seekPreview.value = {
    show: true,
    position: Math.max(0, Math.min(100, position))
  }
}

// 隱藏預覽
const hideSeekPreview = () => {
  seekPreview.value.show = false
}

// 跳轉到指定位置
const seekTo = (event) => {
  const rect = event.target.getBoundingClientRect()
  const position = (event.clientX - rect.left) / rect.width
  const targetIndex = Math.floor(position * audioQueue.value.length)
  
  // 更新播放位置
  podcastStore.seekTo(targetIndex)
}
</script>

<style scoped>
.scrollable-content {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  overflow-x: hidden;  /* 防止水平滾動條 */
  margin: 0 -1rem;  /* 抵消 padding，確保內容對齊 */
  padding: 0 1rem;  /* 添加內邊距，避免內容貼邊 */
}

/* 添加滾動條樣式 */
.scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.scrollable-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.scrollable-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.scrollable-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 這是音訊播放器的進度條樣式設定 */
input[type="range"] {
  -webkit-appearance: none;  /* 移除預設樣式 */
  -moz-appearance: none;     /* Firefox的預設樣式移除 */
  appearance: none;          /* 標準語法移除預設樣式 */
  background: transparent;   /* 設定背景透明 */
  width: 100%;              /* 設定寬度佔滿容器 */
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  margin-top: -6px;
}

input[type="range"]::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  background: transparent;
}

/* 添加語音指示器的動畫效果 */
@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.fa-volume-up {
  animation: pulse 2s infinite;
}

/* 淡入動畫 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 修改播放中的段落效果 */
.playing-segment {
  position: relative;
  transform: scale(1.02);
  transform-origin: left center;  /* 主持人對話從左側開始放大 */
  transition: all 0.3s ease;
  z-index: 10;  /* 確保放大時在其他內容之上 */
}

/* 來賓對話的放大起點 */
.justify-end .playing-segment {
  transform-origin: right center;
}

/* 移除原本的背景和陰影效果 */
.playing-segment::before {
  display: none;
}

/* 進度指示器動畫 */
@keyframes progress-pulse {
  0% { transform: scale(0.95); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(0.95); opacity: 0.5; }
}

.progress-indicator {
  animation: progress-pulse 2s infinite;
}

/* 音量圖標動畫 */
@keyframes volume-pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.fa-volume-up {
  animation: volume-pulse 2s infinite;
}

/* 播放器容器樣式 */
.player-progress-container {
  height: 12px;
  padding: 4px 0;
  margin: 0 -4px;
}

/* 背景進度條 */
.player-progress-bg {
  position: absolute;
  left: 4px;
  right: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

/* 已播放進度條 */
.player-progress-bar {
  position: absolute;
  left: 4px;
  height: 4px;
  background: linear-gradient(to right, #3b82f6, #60a5fa);
  border-radius: 2px;
  transition: width 0.2s ease;
}

/* 進度條把手 */
.player-progress-handle {
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

/* 預覽指示器 */
.player-preview-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  pointer-events: none;
}

/* 預覽標記線 */
.preview-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.5);
  transform: translateX(-50%);
}

/* 預覽氣泡 */
.preview-bubble {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  padding: 4px 8px;
  background: white;
  color: #1e2235;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 預覽氣泡箭頭 */
.preview-bubble::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: white;
}

/* 懸停效果 */
.player-progress-container:hover {
  .player-progress-handle {
    transform: translateY(-50%) scale(1);
  }
  
  .player-progress-bg,
  .player-progress-bar {
    height: 6px;
  }
}

/* 播放按鈕樣式 */
.play-button {
  @apply w-10 h-10 rounded-full bg-white bg-opacity-10 flex items-center justify-center;
  transition: all 0.2s ease;
}

.play-button:hover {
  @apply bg-opacity-20;
  transform: scale(1.05);
}

.play-button:active {
  transform: scale(0.95);
}

/* 進度區域樣式 */
.progress-area {
  background: #fff;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  transition: all 0.5s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 高度過渡動畫 */
.fade-height-enter-active,
.fade-height-leave-active {
  transition: all 0.5s ease;
  max-height: 200px;
  opacity: 1;
  margin-bottom: 1rem;
}

.fade-height-enter-from,
.fade-height-leave-to {
  max-height: 0;
  opacity: 0;
  margin-bottom: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* 淡出效果 */
.fade-out {
  opacity: 0;
  transform: translateY(-10px);
}

/* 閃爍動畫 */
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-blink {
  animation: blink 1.5s ease-in-out infinite;
}
</style> 