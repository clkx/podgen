import { defineStore } from 'pinia'

export const useCharacterStore = defineStore('character', {
  state: () => ({
    host: {
      name: '小志',
      background: '小志是一位資深科技記者，擁有豐富的科技新聞採訪經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的科技議題轉化為聽眾容易理解的內容。',
      voice: {
        name: 'zh-TW-HsiaoChenNeural',
        speed: 1.0,
        pitch: 0
      }
    },
    guest: {
      name: '大目博士',
      background: '大目博士是一位資深的人工智能專家，擁有豐富的人工智能研究經驗，擅長以輕鬆有趣的方式解釋複雜的科技議題，並將其轉化為聽眾容易理解的內容。',
      voice: {
        name: 'zh-TW-YunJheNeural',
        speed: 1.0,
        pitch: 0
      }
    },
    voiceSettings: {
      azure: {
        host: null,
        guest: null
      },
      fish: {
        host: null,
        guest: null
      },
      activeService: 'azure'
    }
  }),

  actions: {
    // 更新角色設定
    updateSettings(settings) {
      if (settings.host) {
        this.host = {
          ...this.host,
          ...settings.host,
          voice: {
            ...this.host.voice,
            ...settings.host.voice
          }
        }
      }
      if (settings.guest) {
        this.guest = {
          ...this.guest,
          ...settings.guest,
          voice: {
            ...this.guest.voice,
            ...settings.guest.voice
          }
        }
      }
      // 儲存到 localStorage
      this.saveToLocalStorage()
    },

    // 更新語音設定
    updateVoiceSettings(settings) {
      this.voiceSettings = {
        ...this.voiceSettings,
        ...settings
      }

      // 根據當前選擇的服務更新角色的語音設定
      const service = settings.activeService
      if (service === 'azure') {
        if (settings.azure.host) {
          this.host.voice = {
            name: settings.azure.host.name,
            speed: 1.0,
            pitch: 0
          }
        }
        if (settings.azure.guest) {
          this.guest.voice = {
            name: settings.azure.guest.name,
            speed: 1.0,
            pitch: 0
          }
        }
      } else if (service === 'fish') {
        if (settings.fish.host) {
          this.host.voice = {
            name: settings.fish.host.id,
            speed: 1.0,
            pitch: 0,
            service: 'fish'
          }
        }
        if (settings.fish.guest) {
          this.guest.voice = {
            name: settings.fish.guest.id,
            speed: 1.0,
            pitch: 0,
            service: 'fish'
          }
        }
      }

      // 儲存到 localStorage
      this.saveToLocalStorage()
    },

    // 載入語音設定
    loadVoiceSettings() {
      const settings = localStorage.getItem('podgen_voice_settings')
      if (settings) {
        const parsed = JSON.parse(settings)
        this.voiceSettings = {
          ...this.voiceSettings,
          ...parsed
        }
        return parsed
      }
      return this.voiceSettings
    },

    // 儲存到 localStorage
    saveToLocalStorage() {
      localStorage.setItem('podgen_character_settings', JSON.stringify({
        host: this.host,
        guest: this.guest
      }))
      localStorage.setItem('podgen_voice_settings', JSON.stringify(this.voiceSettings))
    }
  }
}) 