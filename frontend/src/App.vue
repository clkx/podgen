<template>
  <div class="min-h-screen flex flex-col">
    <!-- 頂部導覽欄 (首頁或行動版) -->
    <nav v-if="isHomePage || isMobile" class="bg-white shadow-md">
      <div class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <div class="flex items-center space-x-4">
            <span class="text-2xl font-bold text-blue-600">PodGen AI</span>
            <span class="text-gray-500 text-sm hidden sm:inline">用AI生成高品質Podcast內容</span>
          </div>
          
          <!-- 導覽連結 (電腦版) -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link to="/podcast-generator" class="nav-link">
              <i class="fas fa-podcast mr-2"></i>開始生成
            </router-link>
            <router-link to="/background-setting" class="nav-link">
              <i class="fas fa-user-circle mr-2"></i>背景設定
            </router-link>
            <router-link to="/voice-customization" class="nav-link">
              <i class="fas fa-microphone-alt mr-2"></i>語音設定
            </router-link>
          </div>

          <!-- 手機版選單按鈕 -->
          <button @click="isMobileMenuOpen = true" class="md:hidden text-gray-600">
            <i class="fas fa-bars text-xl"></i>
          </button>
        </div>
      </div>

      <!-- 手機版選單 -->
      <div v-if="isMobileMenuOpen" 
           class="md:hidden fixed inset-0 bg-gray-800 bg-opacity-50 z-50"
           @click="isMobileMenuOpen = false">
        <div class="bg-white w-64 h-full absolute right-0 p-4" @click.stop>
          <div class="flex justify-between items-center mb-6">
            <span class="text-xl font-bold text-blue-600">PodGen AI</span>
            <button @click="isMobileMenuOpen = false" class="text-gray-600">
              <i class="fas fa-times text-xl"></i>
            </button>
          </div>
          <div class="flex flex-col space-y-4">
            <router-link 
              v-for="item in navItems" 
              :key="item.path"
              :to="item.path" 
              class="nav-link-mobile"
              @click="isMobileMenuOpen = false"
            >
              <i :class="item.icon" class="mr-3 w-6"></i>
              {{ item.name }}
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- 側邊導覽欄 (電腦版非首頁) -->
    <div v-if="!isHomePage && !isMobile" class="flex flex-1">
      <nav class="w-20 bg-gradient-to-b from-[#1e2235] to-[#2c3e50] flex flex-col items-center py-4 space-y-8">
        <router-link to="/" class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-[#1e2235] text-2xl shadow-lg">
          🎛
        </router-link>
        
        <router-link to="/podcast-generator" class="nav-icon">
          <i class="fas fa-podcast"></i>
        </router-link>
        
        <router-link to="/background-setting" class="nav-icon">
          <i class="fas fa-user-circle"></i>
        </router-link>
        
        <router-link to="/voice-customization" class="nav-icon">
          <i class="fas fa-microphone-alt"></i>
        </router-link>
        
        <button class="nav-icon">
          <i class="fas fa-cog"></i>
        </button>
      </nav>

      <!-- 主內容區域 -->
      <div class="flex-1 flex flex-col">
        <router-view></router-view>
      </div>
    </div>

    <!-- 主內容區域 (首頁或行動版) -->
    <template v-else>
      <router-view></router-view>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMobileMenuOpen = ref(false)
const isMobile = ref(false)

// 判斷是否為首頁
const isHomePage = computed(() => route.name === 'home')

// 檢查視窗寬度
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// 監聽視窗大小變化
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 導覽項目
const navItems = [
  { 
    path: '/podcast-generator', 
    name: '開始生成',
    icon: 'fas fa-podcast'
  },
  { 
    path: '/background-setting', 
    name: '背景設定',
    icon: 'fas fa-user-circle'
  },
  { 
    path: '/voice-customization', 
    name: '語音設定',
    icon: 'fas fa-microphone-alt'
  }
]
</script>

<style scoped>
.nav-icon {
  width: 3rem;
  height: 3rem;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s;
}

.nav-icon:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-link {
  @apply text-gray-600 hover:text-blue-600 transition-colors duration-300 flex items-center;
}

.nav-link-mobile {
  @apply text-gray-600 hover:text-blue-600 transition-colors duration-300 py-2 px-4 rounded-lg hover:bg-blue-50 flex items-center;
}
</style>
