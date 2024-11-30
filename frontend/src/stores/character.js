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
      if (settings.host) {
        this.host.voice = {
          ...this.host.voice,
          ...settings.host
        }
      }
      if (settings.guest) {
        this.guest.voice = {
          ...this.guest.voice,
          ...settings.guest
        }
      }
      // 儲存到 localStorage
      this.saveToLocalStorage()
    },

    // 儲存到 localStorage
    saveToLocalStorage() {
      localStorage.setItem('podgen_character_settings', JSON.stringify({
        host: this.host,
        guest: this.guest
      }))
    },

    // 從 localStorage 載入設定
    loadSettings() {
      const settings = localStorage.getItem('podgen_character_settings')
      if (settings) {
        const parsed = JSON.parse(settings)
        // 合併預設值和儲存的設定
        if (parsed.host) {
          this.host = {
            ...this.host,
            ...parsed.host,
            voice: {
              ...this.host.voice,
              ...parsed.host.voice
            }
          }
        }
        if (parsed.guest) {
          this.guest = {
            ...this.guest,
            ...parsed.guest,
            voice: {
              ...this.guest.voice,
              ...parsed.guest.voice
            }
          }
        }
      }
    }
  }
}) 