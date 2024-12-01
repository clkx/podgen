import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const azureService = {
  /**
   * 取得所有可用的語音列表
   */
  async listVoices() {
    try {
      const response = await apiClient.get('/api/azure/voices')
      return response.data
    } catch (error) {
      console.error('Failed to fetch Azure voices:', error)
      throw new Error(error.response?.data?.detail || '無法取得語音列表')
    }
  },

  /**
   * 試聽語音
   */
  async previewSpeech(params) {
    try {
      const response = await apiClient.post('/api/azure/preview', {
        text: params.text,
        voice_name: params.voice_name
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