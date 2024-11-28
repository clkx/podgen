import { createRouter, createWebHistory } from 'vue-router'
import PodcastGeneratorView from '../views/PodcastGeneratorView.vue'
import BackgroundSettingView from '../views/BackgroundSettingView.vue'
import VoiceCustomizationView from '../views/VoiceCustomizationView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
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
    }
  ]
})

export default router