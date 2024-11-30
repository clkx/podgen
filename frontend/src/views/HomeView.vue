<template>
  <div class="flex-1">
    <!-- Hero Section with CTA Input -->
    <section class="pt-20 pb-24 gradient-bg">
      <div class="container mx-auto px-6 text-center">
        <h1 class="text-2xl md:text-6xl font-bold text-white mb-4">生成您的專屬Podcast！</h1>
        <p class="text-3xl text-white mb-8">利用AI將您的創意轉化為引人入勝的Podcast</p>
        <div class="max-w-3xl mx-auto">
          <div class="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-4">
            <input 
              v-model="podcastIdea"
              type="text" 
              placeholder="輸入您的Podcast主題或想法" 
              class="w-full md:w-2/3 px-4 py-3 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-300"
              @keyup.enter="startGenerate"
              :class="{ 'border-red-300': showError }"
            >
            <button 
              @click="startGenerate"
              class="w-full md:w-auto bg-white text-blue-600 font-bold py-3 px-8 rounded-full hover:bg-blue-100 transition duration-300 hover-scale"
              :disabled="!podcastIdea.trim()"
            >
              <span v-if="!podcastIdea.trim()">請輸入主題</span>
              <span v-else>立即生成</span>
            </button>
          </div>
          <p v-if="showError" class="text-red-500 text-sm mt-2">
            請輸入主題內容
          </p>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20">
      <div class="container mx-auto px-6">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">主要功能</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div class="bg-white p-6 rounded-lg shadow-md hover-scale">
            <i class="fas fa-magic text-4xl text-blue-500 mb-4"></i>
            <h3 class="text-xl font-semibold mb-2">一鍵生成Podcast內容</h3>
            <p class="text-gray-600">只需輸入您的想法，AI就能為您生成完整的Podcast內容</p>
          </div>
          <div class="bg-white p-6 rounded-lg shadow-md hover-scale">
            <i class="fas fa-music text-4xl text-blue-500 mb-4"></i>
            <h3 class="text-xl font-semibold mb-2">自動配樂與主題分析</h3>
            <p class="text-gray-600">自動生成適合您內容的背景音樂，並提供深入的主題分析</p>
          </div>
          <div class="bg-white p-6 rounded-lg shadow-md hover-scale">
            <i class="fas fa-sliders-h text-4xl text-blue-500 mb-4"></i>
            <h3 class="text-xl font-semibold mb-2">高度自訂化的設定選項</h3>
            <p class="text-gray-600">根據您的喜好客製語音、人設和背景知識，打造獨一無二的Podcast</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works Section -->
    <section class="py-20 bg-gray-100">
      <div class="container mx-auto px-6">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">如何使用</h2>
        <div class="flex flex-col md:flex-row justify-center items-center space-y-8 md:space-y-0 md:space-x-12">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">1</div>
            <h3 class="font-semibold mb-2">輸入想法</h3>
            <p class="text-gray-600">在文本框中輸入您的Podcast主題或大綱</p>
          </div>
          <i class="fas fa-arrow-right text-3xl text-blue-500 hidden md:block"></i>
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">2</div>
            <h3 class="font-semibold mb-2">AI生成內容</h3>
            <p class="text-gray-600">我們的AI系統會根據您的輸入生成完整的Podcast內容</p>
          </div>
          <i class="fas fa-arrow-right text-3xl text-blue-500 hidden md:block"></i>
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">3</div>
            <h3 class="font-semibold mb-2">編輯與發布</h3>
            <p class="text-gray-600">審核、編輯生成的內容，然後一鍵發布您的Podcast</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="py-20">
      <div class="container mx-auto px-6">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">用戶推薦</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div class="bg-white p-6 rounded-lg shadow-md hover-scale">
            <div class="flex items-center mb-4">
              <img src="https://replicate.delivery/yhqm/a7jpRdI3d8roMlnD56nUei8GfyhGYBpPvWmSBPOmAc3MK1ZTA/out-0.png" alt="用戶頭像" class="w-12 h-12 rounded-full mr-4">
              <div>
                <h4 class="font-semibold">Sarah Chen</h4>
                <p class="text-gray-600">獨立Podcast製作人</p>
              </div>
            </div>
            <p class="text-gray-700">"這款工具讓我輕鬆生成了高質量的Podcast，節省了大量時間！現在我可以更專注於內容創意與聽眾互動。"</p>
          </div>
          <div class="bg-white p-6 rounded-lg shadow-md hover-scale">
            <div class="flex items-center mb-4">
              <img src="https://replicate.delivery/yhqm/kJWeC63ZjZ1bMaoVsRuby4hXuqRpD6NJHktS35dFeFzLK1ZTA/out-0.png" alt="用戶頭像" class="w-12 h-12 rounded-full mr-4">
              <div>
                <h4 class="font-semibold">Michael Lee</h4>
                <p class="text-gray-600">科技博主</p>
              </div>
            </div>
            <p class="text-gray-700">"PodCraft AI的自動配樂功能太棒了！它總能為我的科技話題選擇恰到好處的背景音樂，大大提升了節目的專業感。"</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const podcastIdea = ref('')
const showError = ref(false)

const startGenerate = () => {
  if (!podcastIdea.value.trim()) {
    showError.value = true
    setTimeout(() => {
      showError.value = false
    }, 3000)
    return
  }
  
  showError.value = false
  // 導航到生成頁面並傳遞主題
  router.push({
    path: '/podcast-generator',
    query: { topic: podcastIdea.value.trim() }
  })
}
</script>

<style scoped>
.gradient-bg {
  background: linear-gradient(135deg, #26c6da, #2196f3);
}

.hover-scale {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-scale:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
</style> 