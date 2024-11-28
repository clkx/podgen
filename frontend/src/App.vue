<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <nav class="w-20 bg-gradient-to-b from-[#1e2235] to-[#2c3e50] flex flex-col items-center py-4 space-y-8">
      <router-link to="/" class="w-12 h-12 bg-white rounded-full flex items-center justify-center text-[#1e2235] text-2xl shadow-lg">
        🎛️
      </router-link>
      
      <router-link to="/character-setting" class="nav-icon">
        <i class="fas fa-microphone"></i>
      </router-link>
      
      <router-link to="/voice-customization" class="nav-icon">
        <i class="fas fa-file-alt"></i>
      </router-link>
      
      <router-link to="/podcast-generator" class="nav-icon">
        <i class="fas fa-music"></i>
      </router-link>
      
      <button class="nav-icon">
        <i class="fas fa-cog"></i>
      </button>
    </nav>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <header class="bg-white shadow-sm p-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <span class="text-2xl font-bold text-blue-600">PodGen AI</span>
          <span class="text-gray-500 text-sm">用AI生成高品質Podcast內容</span>
        </div>
        
        <div class="flex items-center space-x-6">
          <div class="flex items-center space-x-3">
            <SocialLinks />
          </div>
        </div>
      </header>

      <!-- Router View -->
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import SocialLinks from '@/components/SocialLinks.vue'
import { useCharacterStore } from '@/stores/character'

const characterStore = useCharacterStore()

// 在應用啟動時載入設定
characterStore.loadSettings()
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
</style>
