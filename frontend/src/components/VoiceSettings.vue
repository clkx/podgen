<template>
  <div class="flex-1 p-6">
    <div class="bg-white rounded-lg shadow-md p-6 flex flex-col">
      <!-- 頁面標題 -->
      <div class="mb-6">
        <h2 class="text-2xl font-semibold">語音設定</h2>
        <p class="text-gray-600 mt-2">
          選擇主持人和來賓的語音，您可以透過試聽功能來確認語音效果。
        </p>
      </div>

      <!-- 服務選擇 Tabs -->
      <div class="mb-6">
        <div class="border-b border-gray-200">
          <nav class="flex" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="switchTab(tab.id)"
              class="flex-1 group relative py-4 px-1 text-center text-sm font-medium hover:bg-gray-50 focus:z-10 focus:outline-none transition-all duration-200"
              :class="[
                currentTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-500'
                  : 'text-gray-500 hover:text-gray-700 border-b-2 border-transparent'
              ]"
            >
              <div class="flex items-center justify-center space-x-2">
                <i :class="tab.icon" class="text-lg"></i>
                <span>{{ tab.name }}</span>
                <span 
                  v-if="tab.status === 'beta'"
                  class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800"
                >
                  Beta
                </span>
              </div>
            </button>
          </nav>
        </div>
      </div>

      <!-- 主要內容區 -->
      <div class="flex-1 flex flex-col min-h-0">
        <!-- 搜尋和已選擇區域 -->
        <div class="sticky top-0 z-10 bg-white space-y-4 mb-4">
          <!-- 搜尋欄 -->
          <div class="relative">
            <input 
              v-model="searchQuery"
              type="text"
              :placeholder="currentTab === 'azure' ? '搜尋語音...' : '搜尋語音模型...'"
              class="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
            <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          </div>

          <!-- 已選擇的語音 -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-center justify-between">
              <!-- 主持人語音 -->
              <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-500">主持人語音：</span>
                <div v-if="currentSelection.host" class="flex items-center space-x-2">
                  <span class="font-medium">{{ getVoiceName(currentSelection.host) }}</span>
                  <button 
                    @click="previewSelection('host')"
                    class="text-blue-600 hover:text-blue-700"
                    :disabled="isPreviewPlaying"
                  >
                    <i :class="isPreviewingHost ? 'fas fa-spinner fa-spin' : 'fas fa-play'"></i>
                  </button>
                  <button 
                    @click="clearSelection('host')"
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <span v-else class="text-gray-400">未選擇</span>
              </div>

              <!-- 來賓語音 -->
              <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-500">來賓語音：</span>
                <div v-if="currentSelection.guest" class="flex items-center space-x-2">
                  <span class="font-medium">{{ getVoiceName(currentSelection.guest) }}</span>
                  <button 
                    @click="previewSelection('guest')"
                    class="text-blue-600 hover:text-blue-700"
                    :disabled="isPreviewPlaying"
                  >
                    <i :class="isPreviewingGuest ? 'fas fa-spinner fa-spin' : 'fas fa-play'"></i>
                  </button>
                  <button 
                    @click="clearSelection('guest')"
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <span v-else class="text-gray-400">未選擇</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 語音列表 -->
        <div class="flex-1 min-h-0 flex flex-col">
          <!-- 列表內容 -->
          <div class="flex-1 overflow-auto">
            <TransitionGroup 
              name="list" 
              tag="div"
              class="space-y-2"
            >
              <!-- Azure TTS 列表 -->
              <template v-if="currentTab === 'azure'">
                <!-- 載入中提示 -->
                <div 
                  v-if="isLoadingAzureVoices" 
                  class="flex justify-center items-center py-4"
                >
                  <i class="fas fa-spinner fa-spin text-blue-500 mr-2"></i>
                  <span class="text-gray-600">載入中...</span>
                </div>

                <!-- 無資料提示 -->
                <div 
                  v-else-if="!filteredAzureVoices.length" 
                  class="flex flex-col items-center justify-center py-8 text-gray-500"
                >
                  <i class="fas fa-inbox text-4xl mb-2"></i>
                  <p>沒有找到符合的語音</p>
                </div>

                <!-- 語音列表 -->
                <div 
                  v-else
                  v-for="voice in filteredAzureVoices" 
                  :key="voice.id"
                  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-200"
                  :class="{
                    'border-blue-500 bg-blue-50': isVoiceSelected(voice)
                  }"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <i class="fas fa-microphone text-blue-500 text-lg"></i>
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900">{{ voice.name }}</h4>
                      <div class="flex items-center space-x-2 mt-1">
                        <span class="text-sm text-gray-500">{{ voice.gender }}</span>
                        <div class="flex items-center space-x-1">
                          <span 
                            v-if="isHostVoice(voice)"
                            class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs"
                          >
                            主持人
                          </span>
                          <span 
                            v-if="isGuestVoice(voice)"
                            class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs"
                          >
                            來賓
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex items-center space-x-3">
                    <button 
                      @click="previewVoice(voice)"
                      class="w-10 h-10 flex items-center justify-center text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                      :class="{ 'opacity-50 cursor-not-allowed': isPreviewPlaying }"
                      :disabled="isPreviewPlaying"
                    >
                      <i :class="isPreviewingVoice(voice) ? 'fas fa-spinner fa-spin' : 'fas fa-play'"></i>
                    </button>

                    <div class="relative group">
                      <button 
                        class="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200 flex items-center space-x-2"
                        :class="{
                          'text-blue-600 border-blue-200 bg-blue-50': isVoiceSelected(voice)
                        }"
                      >
                        <span>設定角色</span>
                        <i class="fas fa-chevron-down text-xs"></i>
                      </button>

                      <div class="absolute right-0 mt-1 w-36 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-20">
                        <button 
                          @click="selectVoice('host', voice)"
                          class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm first:rounded-t-lg flex items-center"
                          :class="{
                            'text-blue-600 bg-blue-50': isHostVoice(voice)
                          }"
                        >
                          <i class="fas fa-check mr-2" :class="{ 'invisible': !isHostVoice(voice) }"></i>
                          設為主持人
                        </button>
                        <button 
                          @click="selectVoice('guest', voice)"
                          class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm last:rounded-b-lg flex items-center"
                          :class="{
                            'text-blue-600 bg-blue-50': isGuestVoice(voice)
                          }"
                        >
                          <i class="fas fa-check mr-2" :class="{ 'invisible': !isGuestVoice(voice) }"></i>
                          設為來賓
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- Fish Audio 列表 -->
              <template v-else>
                <div 
                  v-for="model in currentPageModels" 
                  :key="model.id"
                  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-200"
                  :class="{
                    'border-blue-500 bg-blue-50': isModelSelected(model)
                  }"
                >
                  <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden">
                      <img 
                        :src="getModelImage(model)"
                        :alt="model.title"
                        class="w-full h-full object-cover"
                        @error.once="handleImageError"
                      >
                    </div>
                    <div>
                      <h4 class="font-medium text-gray-900">{{ model.title }}</h4>
                      <div class="flex items-center space-x-3 mt-1">
                        <div class="flex items-center space-x-3 text-sm text-gray-500">
                          <span class="flex items-center">
                            <i class="fas fa-heart text-pink-500 mr-1"></i>
                            {{ formatNumber(model.like_count) }}
                          </span>
                          <span class="flex items-center">
                            <i class="fas fa-bookmark text-yellow-500 mr-1"></i>
                            {{ formatNumber(model.mark_count) }}
                          </span>
                        </div>
                        <div class="flex items-center space-x-1">
                          <span 
                            v-if="isHostModel(model)"
                            class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs"
                          >
                            主持人
                          </span>
                          <span 
                            v-if="isGuestModel(model)"
                            class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs"
                          >
                            來賓
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex items-center space-x-3">
                    <button 
                      @click="previewModel(model)"
                      class="w-10 h-10 flex items-center justify-center text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                      :class="{ 'opacity-50 cursor-not-allowed': isPreviewPlaying }"
                      :disabled="isPreviewPlaying"
                    >
                      <i :class="isPreviewingModel(model) ? 'fas fa-spinner fa-spin' : 'fas fa-play'"></i>
                    </button>

                    <div class="relative group">
                      <button 
                        class="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200 flex items-center space-x-2"
                        :class="{
                          'text-blue-600 border-blue-200 bg-blue-50': isModelSelected(model)
                        }"
                      >
                        <span>設定角色</span>
                        <i class="fas fa-chevron-down text-xs"></i>
                      </button>

                      <div class="absolute right-0 mt-1 w-36 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-20">
                        <button 
                          @click="selectModel('host', model)"
                          class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm first:rounded-t-lg flex items-center"
                          :class="{
                            'text-blue-600 bg-blue-50': isHostModel(model)
                          }"
                        >
                          <i class="fas fa-check mr-2" :class="{ 'invisible': !isHostModel(model) }"></i>
                          設為主持人
                        </button>
                        <button 
                          @click="selectModel('guest', model)"
                          class="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm last:rounded-b-lg flex items-center"
                          :class="{
                            'text-blue-600 bg-blue-50': isGuestModel(model)
                          }"
                        >
                          <i class="fas fa-check mr-2" :class="{ 'invisible': !isGuestModel(model) }"></i>
                          設為來賓
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 載入中提示 -->
                <div 
                  v-if="isLoadingModels" 
                  class="flex justify-center items-center py-4"
                >
                  <i class="fas fa-spinner fa-spin text-blue-500 mr-2"></i>
                  <span class="text-gray-600">載入中...</span>
                </div>

                <!-- 無資料提示 -->
                <div 
                  v-else-if="!currentPageModels.length" 
                  class="flex flex-col items-center justify-center py-8 text-gray-500"
                >
                  <i class="fas fa-inbox text-4xl mb-2"></i>
                  <p>沒有找到符合的語音模型</p>
                </div>
              </template>
            </TransitionGroup>
          </div>

          <!-- 分頁控制 -->
          <div 
            v-if="currentTab === 'fish' && totalPages > 0"
            class="mt-4 px-4 py-3 flex items-center justify-between border-t border-gray-200 bg-white"
          >
            <!-- 分頁資訊 -->
            <div class="flex-1 flex justify-between items-center">
              <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-700">每頁顯示：</span>
                <select 
                  v-model="pageSize" 
                  class="border border-gray-300 rounded-md text-sm"
                  @change="goToPage(1)"
                >
                  <option :value="10">10</option>
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
              </div>
              
              <p class="text-sm text-gray-700">
                顯示第
                <span class="font-medium">{{ startIndex + 1 }}</span>
                至
                <span class="font-medium">{{ endIndex }}</span>
                項，共
                <span class="font-medium">{{ totalItems }}</span>
                項結果
              </p>
            </div>

            <!-- 分頁按鈕 -->
            <div class="mt-4 sm:mt-0">
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <!-- 上一頁 -->
                <button
                  type="button"
                  @click="previousPage"
                  :disabled="currentPage === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">上一頁</span>
                  <i class="fas fa-chevron-left text-xs"></i>
                </button>

                <!-- 頁碼 -->
                <template v-for="page in displayedPages" :key="page">
                  <button
                    type="button"
                    v-if="page !== '...'"
                    @click="goToPage(page)"
                    :class="[
                      'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                      currentPage === page
                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    ]"
                  >
                    {{ page }}
                  </button>
                  <span
                    v-else
                    class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
                  >
                    ...
                  </span>
                </template>

                <!-- 下一頁 -->
                <button
                  type="button"
                  @click="nextPage"
                  :disabled="currentPage === totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">下一頁</span>
                  <i class="fas fa-chevron-right text-xs"></i>
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>

      <!-- 儲存按鈕 -->
      <button 
        @click="saveSettings" 
        class="mt-6 w-full bg-gradient-to-r from-[#26c6da] to-[#2196f3] text-white py-3 rounded-lg hover:from-[#2196f3] hover:to-[#26c6da] transition-all duration-300 flex items-center justify-center"
        :disabled="isSaving"
      >
        <i :class="isSaving ? 'fas fa-spinner fa-spin' : 'fas fa-save'" class="mr-2"></i>
        {{ isSaving ? '儲存中...' : '儲存設定' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useCharacterStore } from '@/stores/character'
import { fishAudioService } from '@/services/fishAudio'
import { azureService } from '@/services/azure'
import { debounce } from 'lodash-es'
import { useRoute, useRouter } from 'vue-router'

const characterStore = useCharacterStore()
const route = useRoute()
const router = useRouter()

// 基本狀態
const currentTab = ref('azure')
const searchQuery = ref('')
const isPreviewPlaying = ref(false)
const previewingId = ref(null)
const isSaving = ref(false)
const listContainer = ref(null)

// Tabs 設定
const tabs = [
  { 
    id: 'azure', 
    name: 'Azure TTS',
    icon: 'fab fa-microsoft',
    status: 'active'
  },
  { 
    id: 'fish', 
    name: 'Fish Audio',
    icon: 'fas fa-fish',
    status: 'beta'
  }
]

// 語音擇狀態
const selections = ref({
  azure: {
    host: null,
    guest: null
  },
  fish: {
    host: null,
    guest: null
  }
})

// 當前選擇的計算屬性
const currentSelection = computed(() => selections.value[currentTab.value])

// Azure 語音相關
const azureVoices = ref([
  { id: 'xiaozhen', name: '曉臻', gender: '女性', type: 'azure' },
  { id: 'xiaoyu', name: '曉雨', gender: '女性', type: 'azure' },
  { id: 'yunzhe', name: '雲哲', gender: '男性', type: 'azure' }
])

// 圖片相關
const defaultImage = '/placeholder.png'
const imageCache = new Map()

const getModelImage = (model) => {
  if (!model.cover_image) return defaultImage
  
  // 如果已經有快取的圖片 URL，直接返回
  if (imageCache.has(model.id)) {
    return imageCache.get(model.id)
  }
  
  // 構建完整的圖片 URL
  const imageUrl = model.cover_image.startsWith('http') 
    ? model.cover_image 
    : `https://public-platform.r2.fish.audio/${model.cover_image}`
  
  // 快取圖片 URL
  imageCache.set(model.id, imageUrl)
  return imageUrl
}

const handleImageError = (event) => {
  // 只在圖片載入失敗時替換一次
  event.target.src = defaultImage
}

// Fish Audio 相關狀態
const fishModels = ref([])
const isLoadingModels = ref(false)
const currentPage = ref(1)
const hasMoreModels = ref(true)
const isInitialized = ref(false)
const isScrolling = ref(false)

// 分頁相關狀態
const pageSize = ref(20)
const totalItems = ref(0)

// 計算屬性
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))
const startIndex = computed(() => (currentPage.value - 1) * pageSize.value)
const endIndex = computed(() => Math.min(startIndex.value + pageSize.value, totalItems.value))

// 當前頁面的模型
const currentPageModels = computed(() => {
  if (currentTab.value === 'azure') {
    return filteredAzureVoices.value
  }
  return fishModels.value
})

// 計算要顯示的頁碼
const displayedPages = computed(() => {
  const pages = []
  const maxPages = 7 // 最多顯示的頁碼數
  const halfMaxPages = Math.floor(maxPages / 2)
  
  if (totalPages.value <= maxPages) {
    // 如果總頁數小於等於最大顯示數，顯示所有頁碼
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    // 總是顯示第一頁
    pages.push(1)
    
    // 計算中間要顯示的頁碼
    let start = Math.max(currentPage.value - halfMaxPages, 2)
    let end = Math.min(start + maxPages - 3, totalPages.value - 1)
    
    if (start > 2) pages.push('...')
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    
    if (end < totalPages.value - 1) pages.push('...')
    
    // 總是顯示最後一頁
    pages.push(totalPages.value)
  }
  
  return pages
})

// 載入 Fish Audio 模型
const loadFishModels = async () => {
  if (isLoadingModels.value) return
  
  try {
    console.log('開始載入 Fish Audio 模型')
    console.log('參數:', {
      page_number: currentPage.value,
      page_size: pageSize.value,
      language: 'zh',
      title: searchQuery.value,
      sort_by: 'like_count'
    })
    
    isLoadingModels.value = true
    
    const response = await fishAudioService.listModels({
      page_number: currentPage.value,
      page_size: pageSize.value,
      language: 'zh',
      title: searchQuery.value,
      sort_by: 'like_count'
    })
    
    console.log('Fish Audio API 回應:', response)
    
    if (response && response.items) {
      fishModels.value = response.items.map(model => ({ ...model, type: 'fish' }))
      totalItems.value = response.total
      console.log('成功載入模型:', fishModels.value.length)
      console.log('總數:', totalItems.value)
    } else {
      console.error('API 回應格式不正確:', response)
    }
    
  } catch (error) {
    console.error('載入語音模型失敗:', error)
    console.error('錯誤詳情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    })
  } finally {
    isLoadingModels.value = false
    isInitialized.value = true
  }
}

// 分頁控制方法
const previousPage = async () => {
  console.log('Previous page clicked, current page:', currentPage.value)
  if (currentPage.value > 1) {
    await goToPage(currentPage.value - 1)
  }
}

const nextPage = async () => {
  console.log('Next page clicked, current page:', currentPage.value, 'total pages:', totalPages.value)
  if (currentPage.value < totalPages.value) {
    await goToPage(currentPage.value + 1)
  }
}

const goToPage = async (page) => {
  console.log('Going to page:', page)
  currentPage.value = page
  updateUrlParams()
  await loadFishModels()
}

// 更新 URL 參數
const updateUrlParams = () => {
  router.replace({
    query: {
      ...route.query,
      page: currentPage.value,
      tab: currentTab.value,
      size: pageSize.value
    }
  })
}

// 監聽搜尋
watch(searchQuery, debounce(() => {
  console.log('搜尋查詢變更:', searchQuery.value)
  if (currentTab.value === 'fish') {
    currentPage.value = 1
    updateUrlParams()
    loadFishModels()
  }
}, 300))

// 監聽標籤切換
watch(currentTab, (newTab) => {
  console.log('切換標籤:', newTab)
  if (newTab === 'fish' && !isInitialized.value) {
    loadFishModels()
  }
})

// 初始化
onMounted(() => {
  console.log('組件掛載')
  // 從 URL 參數恢復狀態
  const { page, tab, size } = route.query
  if (page) {
    currentPage.value = Number(page)
  }
  if (tab) {
    currentTab.value = tab
  }
  if (size) {
    pageSize.value = Number(size)
  }
  
  console.log('初始狀態:', {
    currentTab: currentTab.value,
    currentPage: currentPage.value,
    pageSize: pageSize.value
  })
  
  // 載入初始數據
  if (currentTab.value === 'fish') {
    console.log('初始標籤是 Fish Audio，開始載入模型')
    loadFishModels()
  }
})

// 計算屬性
const filteredAzureVoices = computed(() => {
  if (!searchQuery.value) return azureVoices.value
  const query = searchQuery.value.toLowerCase()
  return azureVoices.value.filter(voice => 
    voice.name.toLowerCase().includes(query) || 
    voice.gender.toLowerCase().includes(query)
  )
})

const filteredFishModels = computed(() => {
  if (!searchQuery.value) return fishModels.value
  const query = searchQuery.value.toLowerCase()
  return fishModels.value.filter(model => 
    model.title.toLowerCase().includes(query)
  )
})

const isPreviewingHost = computed(() => 
  isPreviewPlaying.value && 
  previewingId.value === currentSelection.value?.host?.id
)

const isPreviewingGuest = computed(() => 
  isPreviewPlaying.value && 
  previewingId.value === currentSelection.value?.guest?.id
)

// 方法
const selectVoice = (role, voice) => {
  selections.value.azure[role] = { ...voice, type: 'azure' }
}

const selectModel = (role, model) => {
  selections.value.fish[role] = { ...model, type: 'fish' }
}

const clearSelection = (role) => {
  selections.value[currentTab.value][role] = null
}

const getVoiceName = (voice) => {
  return voice.type === 'azure' ? voice.name : voice.title
}

const previewSelection = async (role) => {
  const selection = currentSelection.value[role]
  if (!selection || isPreviewPlaying.value) return
  
  if (selection.type === 'azure') {
    await previewVoice(selection)
  } else {
    await previewModel(selection)
  }
}

const previewVoice = async (voice) => {
  if (isPreviewPlaying.value) return
  
  try {
    isPreviewPlaying.value = true
    previewingId.value = voice.id
    
    const audioBlob = await azureService.previewSpeech({
      text: '您好，這是一段測試語音，讓您確認語音效果。',
      voice_name: voice.id
    })
    
    await azureService.playAudio(audioBlob)
  } catch (error) {
    console.error('試聽失敗:', error)
  } finally {
    isPreviewPlaying.value = false
    previewingId.value = null
  }
}

const previewModel = async (model) => {
  if (isPreviewPlaying.value) return
  
  try {
    isPreviewPlaying.value = true
    previewingId.value = model.id
    
    const audioBlob = await fishAudioService.previewSpeech({
      text: '您好，這是一段測試語音，讓您確認語音效果。',
      model_id: model.id
    })
    
    await fishAudioService.playAudio(audioBlob)
  } catch (error) {
    console.error('試聽失敗:', error)
  } finally {
    isPreviewPlaying.value = false
    previewingId.value = null
  }
}

// 輔助方法
const isVoiceSelected = (voice) => {
  return selections.value.azure.host?.id === voice.id || 
         selections.value.azure.guest?.id === voice.id
}

const isHostVoice = (voice) => selections.value.azure.host?.id === voice.id
const isGuestVoice = (voice) => selections.value.azure.guest?.id === voice.id

const isModelSelected = (model) => {
  return selections.value.fish.host?.id === model.id || 
         selections.value.fish.guest?.id === model.id
}

const isHostModel = (model) => selections.value.fish.host?.id === model.id
const isGuestModel = (model) => selections.value.fish.guest?.id === model.id

const isPreviewingVoice = (voice) => isPreviewPlaying.value && previewingId.value === voice.id
const isPreviewingModel = (model) => isPreviewPlaying.value && previewingId.value === model.id

const formatNumber = (num) => {
  return new Intl.NumberFormat('zh-TW', { 
    notation: 'compact',
    compactDisplay: 'short'
  }).format(num)
}

const saveSettings = async () => {
  isSaving.value = true
  
  try {
    await characterStore.updateVoiceSettings({
      azure: selections.value.azure,
      fish: selections.value.fish,
      activeService: currentTab.value
    })
  } catch (error) {
    console.error('儲存設定失敗:', error)
  } finally {
    isSaving.value = false
  }
}

// 切換標籤
const switchTab = async (tabId) => {
  console.log('切換標籤:', tabId)
  if (currentTab.value === tabId) return
  
  currentTab.value = tabId
  currentPage.value = 1
  updateUrlParams()
  
  if (tabId === 'fish') {
    console.log('切換到 Fish Audio 標籤，開始載入模型')
    await loadFishModels()
  }
}
</script>

<style>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-move {
  transition: transform 0.3s ease;
}
</style> 