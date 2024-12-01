import axios from 'axios'

// 確保 API_BASE_URL 有正確的值
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 創建一個 axios 實例，設定基礎 URL
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const fishAudioService = {
  /**
   * 取得所有可用的語音模型列表
   */
  async listModels(params = {}) {
    try {
      const response = await apiClient.get('/api/fish-audio/models', {
        params: {
          page_size: params.page_size || 20,
          page_number: params.page_number || 1,
          title: params.title || '',
          language: params.language,
          sort_by: params.sort_by
        }
      })
      
      return response.data
    } catch (error) {
      console.error('Failed to fetch Fish Audio models:', error)
      throw new Error(error.response?.data?.detail || '無法取得語音模型列表')
    }
  },

  /**
   * 試聽語音
   */
  async previewSpeech(params) {
    try {
      const response = await apiClient.post('/api/fish-audio/preview', {
        text: params.text,
        model_id: params.model_id
      }, {
        responseType: 'blob'
      })
      
      return response.data
    } catch (error) {
      console.error('Failed to preview speech:', error)
      throw new Error(error.response?.data?.detail || '語音預覽失敗')
    }
  },

  /**
   * 生成完整語音
   */
  async synthesize(params) {
    try {
      const response = await apiClient.post('/api/fish-audio/synthesize', {
        text: params.text,
        model_id: params.model_id
      }, {
        responseType: 'blob'
      })
      
      return response.data
    } catch (error) {
      console.error('Failed to synthesize speech:', error)
      throw new Error(error.response?.data?.detail || '語音生成失敗')
    }
  },

  /**
   * 播放音訊 Blob
   */
  async playAudio(audioBlob) {
    try {
      const url = URL.createObjectURL(audioBlob)
      const audio = new Audio(url)
      
      await audio.play()
      
      // 播放完畢後清理 URL
      audio.onended = () => {
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Failed to play audio:', error)
      throw new Error('音訊播放失敗')
    }
  }
} 