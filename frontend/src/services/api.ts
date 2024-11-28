import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 本地儲存相關
const LOCAL_STORAGE_KEYS = {
  CHARACTER_SETTINGS: 'podgen_character_settings',
  VOICE_SETTINGS: 'podgen_voice_settings'
}

// 本地儲存服務
export const localStorageAPI = {
  // 角色設定
  getCharacterSettings: () => {
    const settings = localStorage.getItem(LOCAL_STORAGE_KEYS.CHARACTER_SETTINGS)
    return settings ? JSON.parse(settings) : {
      host: {
        name: 'AI 科技主持人',
        character: '熱愛科技的Podcast主持人，擁有十年以上的科技行業經驗，語氣風格專業但輕鬆幽默'
      },
      guest: {
        name: 'AI 研究專家',
        character: '資深AI研究員，在機器學習領域有豐富經驗，擅長用生活化的例子說明複雜的AI概念'
      }
    }
  },

  saveCharacterSettings: (settings) => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.CHARACTER_SETTINGS, JSON.stringify(settings))
    return Promise.resolve({ success: true })
  },

  // 語音設定
  getVoiceSettings: () => {
    const settings = localStorage.getItem(LOCAL_STORAGE_KEYS.VOICE_SETTINGS)
    return settings ? JSON.parse(settings) : {
      host: {
        speed: 1.0,
        pitch: 0
      },
      guest: {
        speed: 1.0,
        pitch: 0
      }
    }
  },

  saveVoiceSettings: (settings) => {
    localStorage.setItem(LOCAL_STORAGE_KEYS.VOICE_SETTINGS, JSON.stringify(settings))
    return Promise.resolve({ success: true })
  }
}

// Podcast 生成相關 API
export const podcastAPI = {
  generateFromPrompt: (data: {
    prompt: string,
    background_knowledge: string,
    host_name: string,
    host_background: string,
    guest_name: string,
    guest_background: string
  }) => 
    api.post('/generate/prompt', data),
  
  generateFromPDF: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/generate/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  generateFromArxiv: (arxivId: string) => 
    api.post('/generate/arxiv', { arxiv_id: arxivId })
}

// PDF 管理相關 API
export const pdfAPI = {
  uploadPDF: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/pdfs/upload', formData)
  },
  
  deletePDF: (pdfId: string) => 
    api.delete(`/pdfs/${pdfId}`)
}

// 音頻相關 API
export const audioAPI = {
  generateAudio: (data: {
    dialogue: Array<{[key: string]: string}>,
    host_voice?: string,
    guest_voice?: string
  }) => 
    api.post('/api/audio/generate', data),
  
  getSample: (type: string) => 
    api.get(`/audio/sample/${type}`)
} 