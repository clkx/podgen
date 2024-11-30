import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PodcastGeneratorView from '../views/PodcastGeneratorView.vue'
import BackgroundSettingView from '../views/BackgroundSettingView.vue'
import VoiceCustomizationView from '../views/VoiceCustomizationView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/podcast-generator',
      name: 'podcast-generator',
      component: PodcastGeneratorView
    },
    {
      path: '/background-setting',
      name: 'background-setting',
      component: BackgroundSettingView
    },
    {
      path: '/voice-customization',
      name: 'voice-customization',
      component: VoiceCustomizationView
    },
    {
      path: '/settings/voice',
      name: 'voiceSettings',
      component: () => import('../components/VoiceSettings.vue')
    }
  ]
})

export default router
