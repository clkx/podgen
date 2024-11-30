<template>
  <div class="flex-1 p-4 md:p-6 overflow-hidden">
    <div class="flex flex-col md:flex-row md:space-x-6 space-y-6 md:space-y-0 h-full">
      <!-- 左側 - 輸入區域 -->
      <div class="w-full md:w-1/2 bg-white rounded-lg shadow-md p-4 md:p-6 flex flex-col md:max-h-[calc(100vh-120px)]">
        <!-- 固定的頂部區域 -->
        <div class="flex-none">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-semibold">Podcast生成</h2>
          </div>
          <p class="text-gray-600 mb-4">
            輸入您想要討論的主題或想法，由AI自動生成對話腳本與語音，幫助您快速製作出專屬的Podcast內容
          </p>

          <!-- 當有從首頁帶入主題時，顯示提示 -->
          <div v-if="route.query.topic" class="bg-blue-50 p-4 rounded-md mb-4">
            <div class="flex items-center space-x-2">
              <i class="fas fa-info-circle text-blue-500"></i>
              <span class="text-blue-700">
                您可以先調整設定再開始生成，或直接點擊生成按鈕開始
              </span>
            </div>
          </div>

          <!-- 生成方式選擇 -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-600 mb-2">選擇生成方式</label>
            <div class="grid grid-cols-3 gap-3">
              <button
                @click="selectGenerationType('prompt')"
                :disabled="generationStore.isGenerating"
                class="generation-type-btn p-3 border rounded-lg transition-all duration-300"
                :class="[
                  generationType === 'prompt' ? 
                    'border-blue-500 bg-blue-50 text-blue-700' : 
                    'border-gray-300 hover:bg-gray-50 text-gray-700',
                  generationStore.isGenerating ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <i class="fas fa-keyboard mb-2 text-xl"></i>
                <div class="text-sm font-medium">Prompt</div>
                <div class="text-xs text-gray-500 mt-1">自由輸入提示詞</div>
              </button>
              <button
                @click="selectGenerationType('pdf')"
                :disabled="generationStore.isGenerating"
                class="generation-type-btn p-3 border rounded-lg transition-all duration-300"
                :class="[
                  generationType === 'pdf' ? 
                    'border-blue-500 bg-blue-50 text-blue-700' : 
                    'border-gray-300 hover:bg-gray-50 text-gray-700',
                  generationStore.isGenerating ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <i class="fas fa-file-pdf mb-2 text-xl"></i>
                <div class="text-sm font-medium">PDF</div>
                <div class="text-xs text-gray-500 mt-1">上傳 PDF 生成</div>
              </button>
              <button
                @click="selectGenerationType('arxiv')"
                :disabled="generationStore.isGenerating"
                class="generation-type-btn p-3 border rounded-lg transition-all duration-300"
                :class="[
                  generationType === 'arxiv' ? 
                    'border-blue-500 bg-blue-50 text-blue-700' : 
                    'border-gray-300 hover:bg-gray-50 text-gray-700',
                  generationStore.isGenerating ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <i class="fas fa-graduation-cap mb-2 text-xl"></i>
                <div class="text-sm font-medium">arXiv</div>
                <div class="text-xs text-gray-500 mt-1">學術論文轉換</div>
              </button>
            </div>
          </div>
        </div>

        <!-- 可滾動的輸入區域 -->
        <div class="flex-1 overflow-y-auto">
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
        </div>

        <!-- 固定在底部的按鈕 -->
        <div class="flex-none mt-4">
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
      </div>

      <!-- 右側 - 預覽區域 -->
      <div class="w-full md:w-1/2 bg-white rounded-lg shadow-md p-4 md:p-6 flex flex-col md:max-h-[calc(100vh-120px)]">
        <!-- 進度顯示區域 -->
        <div class="flex-none">
          <Transition name="fade-height">
            <div v-if="generationStore.isGenerating || generationStore.progress.stage === 'audio'" 
                 class="progress-area mb-4 bg-white rounded-lg p-3 shadow-sm"
                 :class="{ 'fade-out': fadeOutProgress }">
              <!-- 進度顯示內容 -->
              <div class="flex items-center space-x-4">
                <!-- 當前階段圖標 -->
                <div class="relative">
                  <i class="fas text-lg"
                     :class="{
                       'fa-file-alt text-blue-500': generationStore.progress.stage === 'script',
                       'fa-microphone text-green-500': generationStore.progress.stage === 'audio'
                     }"></i>
                </div>

                <!-- 進度文字 -->
                <div class="flex-1">
                  <div class="flex items-center space-x-2 text-sm">
                    <span class="font-medium">
                      {{ generationStore.progress.stage === 'audio' ? '生成語音' : '生成腳本' }}
                    </span>
                    <span class="text-gray-500">
                      {{ generationStore.progress.message }}
                    </span>
                  </div>
                </div>

                <!-- 進度百分比 -->
                <div class="text-sm font-bold"
                     :class="{
                       'text-blue-500': generationStore.progress.stage === 'script',
                       'text-green-500': generationStore.progress.stage === 'audio'
                     }">
                  {{ generationStore.progress.percentage }}%
                </div>
              </div>
            </div>
          </Transition>

          <!-- 生成完成訊息 -->
          <Transition name="fade">
            <div v-if="generationStore.progress.stage === 'completed'" 
                 class="mb-4 bg-green-50 rounded-lg p-3 text-green-700 flex items-center space-x-2">
              <i class="fas fa-check-circle"></i>
              <span>{{ generationStore.progress.message }}</span>
            </div>
          </Transition>
        </div>

        <!-- 可滾動的對話內容區域 -->
        <div ref="dialogueContainer" 
             class="flex-1 overflow-y-auto relative min-h-[300px] md:min-h-[400px]">
          <!-- 空白狀態 -->
          <div v-if="!segments.length && !generationStore.isGenerating" 
               class="absolute inset-0 flex items-center justify-center">
            <div class="text-center text-gray-500">
              <i class="fas fa-podcast text-4xl mb-4 block"></i>
              <p>選擇生成方式並點擊開始生成</p>
            </div>
          </div>

          <!-- 生成腳本時的載入動畫 -->
          <div v-else-if="generationStore.progress.stage === 'script'"
               class="absolute inset-0 flex items-center justify-center">
            <div class="text-center">
              <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mb-4 mx-auto"></div>
              <p class="text-gray-600">{{ generationStore.progress.message }}</p>
            </div>
          </div>

          <!-- 對話內容顯示 -->
          <div v-else class="h-full space-y-6">
            <TransitionGroup name="fade">
              <div v-for="(segment, index) in segments" 
                   :key="index"
                   :ref="el => { if (index === currentAudioIndex) currentSegmentRef = el }"
                   class="mb-6 relative">
                <!-- 主持人對話 -->
                <div v-if="script?.dialogue[index]?.speaker === script?.host_name" 
                     class="flex items-start space-x-4 transition-all duration-300"
                     :class="{
                       'playing-segment': isPlaying && index === currentAudioIndex,
                       'opacity-50': generationStore.progress.stage === 'audio' && index > currentProgress?.index
                     }">
                  <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-microphone text-blue-500 text-lg"></i>
                  </div>
                  <div class="flex-1 max-w-[85%]">
                    <div class="text-sm text-blue-600 mb-2 flex items-center">
                      <span class="font-medium">{{ script?.host_name }}</span>
                      <span v-if="hasAudio(index)" class="ml-2 text-xs text-green-500">
                        <i class="fas fa-volume-up"></i>
                      </span>
                      <span v-else-if="isCurrentSegment(index)" class="ml-2 text-xs text-blue-500">
                        <i class="fas fa-spinner fa-spin"></i>
                      </span>
                    </div>
                    <div class="bg-blue-50 rounded-lg p-5 text-gray-700 leading-relaxed">
                      {{ segment }}
                    </div>
                  </div>
                </div>

                <!-- 來賓對話 -->
                <div v-else 
                     class="flex items-start justify-end space-x-4 transition-all duration-300"
                     :class="{
                       'playing-segment': isPlaying && index === currentAudioIndex,
                       'opacity-50': generationStore.progress.stage === 'audio' && index > currentProgress?.index
                     }">
                  <div class="flex-1 max-w-[85%]">
                    <div class="text-sm text-green-600 mb-2 text-right flex items-center justify-end">
                      <span class="font-medium">{{ script?.guest_name }}</span>
                      <span v-if="hasAudio(index)" class="ml-2 text-xs text-green-500">
                        <i class="fas fa-volume-up"></i>
                      </span>
                      <span v-else-if="isCurrentSegment(index)" class="ml-2 text-xs text-blue-500">
                        <i class="fas fa-spinner fa-spin"></i>
                      </span>
                    </div>
                    <div class="bg-green-50 rounded-lg p-5 text-gray-700 leading-relaxed">
                      {{ segment }}
                    </div>
                  </div>
                  <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-user text-green-500 text-lg"></i>
                  </div>
                </div>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <!-- 固定在底部的音頻播放器（僅桌面版） -->
        <div class="flex-none mt-4">
          <!-- 音頻播放器 -->
          <div v-if="audioQueue.length > 0" class="bg-[#1e2235] rounded-lg p-4 hidden md:block">
            <!-- 進度條容器 -->
            <div class="player-progress-container mb-4 relative cursor-pointer" 
                 @click="handleProgressClick"
                 @mousedown="startDragging"
                 @mousemove="handleDragging"
                 @mouseup="stopDragging"
                 @mouseleave="stopDragging"
                 ref="progressContainer">
              
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
    </div>
  </div>

  <!-- 行動版迷你播放控制列 -->
  <Transition name="slide-up">
    <div v-if="audioQueue.length > 0" 
         class="md:hidden fixed bottom-0 left-0 right-0 bg-[#1e2235] p-3 z-50 shadow-lg">
      <div class="flex items-center space-x-3">
        <!-- 播放/暫停按鈕 -->
        <button @click="podcastStore.togglePlay" 
                class="w-10 h-10 rounded-full bg-white bg-opacity-10 flex items-center justify-center text-white">
          <i class="fas" :class="isPlaying ? 'fa-pause' : 'fa-play'"></i>
        </button>
        
        <!-- 進度資訊 -->
        <div class="flex-1">
          <!-- 進度條 -->
          <div class="player-progress-container-mini mb-1 relative cursor-pointer"
               @click="handleProgressClick"
               @mousedown="startDragging"
               @mousemove="handleDragging"
               @mouseup="stopDragging"
               @mouseleave="stopDragging"
               ref="progressContainer">
            <div class="player-progress-bg-mini"></div>
            <div class="player-progress-bar-mini"
                 :style="{ width: `${(currentAudioIndex / (audioQueue.length - 1)) * 100}%` }">
            </div>
          </div>
          <!-- 進度文字 -->
          <div class="text-xs text-white text-opacity-80">
            {{ currentAudioIndex + 1 }} / {{ audioQueue.length }}
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import FileUploader from '@/components/FileUploader.vue'
import { podcastAPI } from '@/services/api'
import { useCharacterStore } from '@/stores/character'
import { usePodcastStore } from '@/stores/podcast'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useGenerationStore } from '@/stores/generation'

const podcastStore = usePodcastStore()
const characterStore = useCharacterStore()
const route = useRoute()
const generationStore = useGenerationStore()

// 從 store 中解構需要的狀態
const { 
  isGenerating, 
  progress,
  audioQueue, 
  script, 
  isPlaying,
  currentAudioIndex,
  showProgress,
  fadeOutProgress
} = storeToRefs(podcastStore)

// 基礎狀態
const topic = ref('')
const segments = ref([])
const uploadedPDF = ref(null)
const generationType = ref('prompt')
const arxivId = ref('')
const audioProgress = ref({ current: 0, total: 0 })

// 添加 seekPreview 的定義
const seekPreview = ref({
  show: false,
  position: 0
})

// 進度條控制相關
const progressContainer = ref(null)
const isDragging = ref(false)

// 處理進度條點擊
const handleProgressClick = (event) => {
  if (!progressContainer.value) return
  
  const rect = progressContainer.value.getBoundingClientRect()
  const position = (event.clientX - rect.left) / rect.width
  const targetIndex = Math.floor(position * audioQueue.value.length)
  
  // 使用 store 中的 seekTo 方法跳轉
  podcastStore.seekTo(Math.min(targetIndex, audioQueue.value.length - 1))
}

// 開始拖動
const startDragging = () => {
  isDragging.value = true
}

// 處理拖動
const handleDragging = (event) => {
  if (!isDragging.value || !progressContainer.value) return
  
  const rect = progressContainer.value.getBoundingClientRect()
  const position = ((event.clientX - rect.left) / rect.width) * 100
  seekPreview.value = {
    show: true,
    position: Math.max(0, Math.min(100, position))
  }
}

// 停止拖動
const stopDragging = (event) => {
  if (isDragging.value && progressContainer.value) {
    handleProgressClick(event)
  }
  isDragging.value = false
  seekPreview.value.show = false
}

// 生成類型相關
const selectGenerationType = (type) => {
  generationType.value = type
  // 重置相關數據
  topic.value = ''
  arxivId.value = ''
  uploadedPDF.value = null
}

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
  if (files && files.length > 0) {
    uploadedPDF.value = files[0]
  } else {
    uploadedPDF.value = null
  }
}

// 生成 Podcast
const generatePodcast = async () => {
  if (!canGenerate.value) return
  
  try {
    // 開始生成進度顯示
    showProgress.value = true
    fadeOutProgress.value = false
    
    // 開始生成
    generationStore.startGeneration(generationType.value)

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
    alert(error.message || '生成失敗，請稍後再試')
    generationStore.cleanup()
  }
}

// 從 Prompt 生成
const generateFromPrompt = async () => {
  if (!topic.value.trim()) {
    throw new Error('請輸入主題')
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
    throw new Error(err.message || 'Prompt 生成失敗')
  }
}

// 從 PDF 生成
const generateFromPDF = async () => {
  if (!uploadedPDF.value) {
    throw new Error('請先上傳 PDF 檔案')
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
    throw new Error(err.message || 'PDF 生成失敗')
  }
}

// 從 arXiv 生成
const generateFromArxiv = async () => {
  if (!arxivId.value) {
    throw new Error('請輸入 arXiv URL')
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
    throw new Error(err.message || 'arXiv 生成失敗')
  }
}

// 檢查某個段落是否已有語音
const hasAudio = (index) => {
  return audioQueue.value[index]?.audio !== undefined
}

// 修改模板中的條件判斷
const isCurrentSegment = (index) => {
  return index === currentAudioIndex.value
}

// 監聽路由參數
onMounted(() => {
  // 只填入主題，不自動生成
  if (route.query.topic) {
    topic.value = route.query.topic
    generationType.value = 'prompt'
  }
})

// 生命週期鉤子
onUnmounted(() => {
  generationStore.cleanup()
})

// 在 script setup 部分添加
watch(audioQueue, (newQueue) => {
  if (newQueue && newQueue.length > 0) {
    segments.value = newQueue.map(segment => segment.content)
  }
}, { deep: true })

// 添加對話容器和當前段落的 ref
const dialogueContainer = ref(null)
const currentSegmentRef = ref(null)

// 監聽播放索引變化
watch(() => currentAudioIndex.value, async (newIndex) => {
  if (newIndex === null || newIndex === undefined) return
  
  // 等待 DOM 更新
  await nextTick()
  
  // 獲取當前播放的段落元素
  const currentSegment = currentSegmentRef.value
  if (!currentSegment || !dialogueContainer.value) return

  // 計算滾動位置
  const container = dialogueContainer.value
  const segmentRect = currentSegment.getBoundingClientRect()
  const containerRect = container.getBoundingClientRect()

  // 檢查元素是否在可視區域內
  const isInView = (
    segmentRect.top >= containerRect.top &&
    segmentRect.bottom <= containerRect.bottom
  )

  // 如果不在可視區域內，則滾動到該元素
  if (!isInView) {
    currentSegment.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest'
    })
  }
}, { immediate: true })
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
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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

/* 度指示器動 */
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

/* 美化滾動條 */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
  overflow-x: hidden; /* 防止橫向滾動 */
}

/* 確保對話內容不會超出容器 */
.bg-blue-50,
.bg-green-50 {
  word-break: break-word;
  max-width: 100%;
  white-space: pre-wrap;
}

/* 確保對話框內的文字正確換行 */
.text-gray-700 {
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

/* 修改滾動條樣式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
  height: 0; /* 移除橫向滾動條 */
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 確保對話容器的寬度正確 */
.flex-1 {
  min-width: 0; /* 防止 flex 子元素溢出 */
}

/* 更新樣式 */
.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.leading-relaxed {
  line-height: 1.75;
}

/* 確保對話內容不會超出容器但保持可讀性 */
.text-gray-700 {
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  font-size: 1rem;
  text-align: justify;
}

/* 優化播放中的對話框效果 */
.playing-segment {
  transform: scale(1.01);
  transition: all 0.3s ease;
}

/* 確保容器有適當的內邊距 */
.overflow-y-auto {
  padding: 1rem;
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
  overflow-x: hidden;
}

/* 優化滾動條樣式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
  height: 0;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 添加播放中段落的視覺效果 */
.playing-segment {
  position: relative;
  transform: scale(1.01);
  transition: all 0.3s ease;
  z-index: 2;
}

.playing-segment::before {
  content: '';
  position: absolute;
  inset: -0.5rem;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 1rem;
  z-index: -1;
}

/* 確保滾動行為順暢 */
.overflow-y-auto {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

/* 優化過渡動畫 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 確保容器在所有裝置上都有正確的大小 */
@media (max-width: 768px) {
  .min-h-[300px] {
    min-height: 60vh;
  }
}

@media (min-width: 769px) {
  .md:min-h-[400px] {
    min-height: 70vh;
  }
}

/* 修正 RWD 樣式 */
.min-h-300 {
  min-height: 60vh;
}

.md-min-h-400 {
  min-height: 70vh;
}

@media (max-width: 768px) {
  .min-h-300 {
    min-height: 60vh;
  }
}

@media (min-width: 769px) {
  .md-min-h-400 {
    min-height: 70vh;
  }
}

/* 進度條過渡動畫 */
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

/* 進度條淡出效果 */
.fade-out {
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.5s ease;
}

.progress-area {
  transition: all 0.5s ease;
  border: 1px solid #e5e7eb;
}

/* 生成方式按鈕樣式 */
.generation-type-btn {
  @apply flex flex-col items-center justify-center text-center;
  min-height: 120px;
}

.generation-type-btn:disabled {
  @apply pointer-events-none;
}

.generation-type-btn i {
  @apply block;
}

.generation-type-btn > div {
  @apply w-full text-center;
}

/* 播放器進度條樣式 */
.player-progress-container {
  height: 12px;
  padding: 4px 0;
  margin: 0 -4px;
}

.player-progress-bg {
  position: absolute;
  left: 4px;
  right: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.player-progress-bar {
  position: absolute;
  left: 4px;
  height: 4px;
  background: linear-gradient(to right, #3b82f6, #60a5fa);
  border-radius: 2px;
  transition: width 0.1s ease;
}

.player-progress-handle {
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* 懸停和拖動效果 */
.player-progress-container:hover .player-progress-handle,
.player-progress-container:active .player-progress-handle {
  opacity: 1;
}

.player-progress-container:hover .player-progress-bg,
.player-progress-container:hover .player-progress-bar,
.player-progress-container:active .player-progress-bg,
.player-progress-container:active .player-progress-bar {
  height: 6px;
}

/* 預覽指示器樣式 */
.player-preview-indicator {
  position: absolute;
  top: 0;
  bottom: 0;
  pointer-events: none;
}

.preview-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.5);
  transform: translateX(-50%);
}

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

.preview-bubble::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: white;
}

/* 行動版迷你播放器樣式 */
.player-progress-container-mini {
  height: 8px;
  padding: 2px 0;
  touch-action: none; /* 防止在觸控設備上的滾動干擾 */
}

.player-progress-bg-mini {
  position: absolute;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1.5px;
}

.player-progress-bar-mini {
  position: absolute;
  left: 0;
  height: 3px;
  background: linear-gradient(to right, #3b82f6, #60a5fa);
  border-radius: 1.5px;
  transition: width 0.1s ease;
}

/* 滑入動畫 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), 
              opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

/* 確保內容不會被迷你播放器擋住 */
@media (max-width: 768px) {
  .flex-1.overflow-y-auto {
    padding-bottom: 70px;
  }
}

/* 修正 RWD 樣式 */
.min-h-300 {
  min-height: 60vh;
}

.md-min-h-400 {
  min-height: 70vh;
}

@media (max-width: 768px) {
  .min-h-300 {
    min-height: calc(100vh - 200px);
  }
  
  .flex-1.overflow-y-auto {
    padding-bottom: 70px;
  }
}

@media (min-width: 769px) {
  .md-min-h-400 {
    min-height: 70vh;
  }
}
</style> 