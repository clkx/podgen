import axios from 'axios'

// 基礎 API 設定
const BASE_URL = 'http://localhost:8000'

// Podcast 生成相關 API
export const podcastAPI = {
  generateFromPrompt: (data) => axios.post(`${BASE_URL}/api/generate/prompt`, data),
  generateFromPDF: (formData) => axios.post(`${BASE_URL}/api/generate/pdf`, formData),
  generateFromArxiv: (data) => axios.post(`${BASE_URL}/api/generate/arxiv`, data)
}

// PDF 相關 API
export const pdfAPI = {
  // 上傳 PDF 作為背景知識
  uploadPDF: (formData) => axios.post(`${BASE_URL}/api/upload/pdf`, formData),
  
  // 上傳臨時 PDF 用於生成
  uploadTempPDF: (formData) => axios.post(`${BASE_URL}/api/upload/pdf`, {
    ...formData,
    is_temporary: true
  }),
  
  // 獲取已上傳的 PDF 列表
  getPDFList: () => axios.get(`${BASE_URL}/api/references`),
  
  // 刪除已上傳的 PDF
  deletePDF: (foldername) => axios.delete(`${BASE_URL}/api/reference/${foldername}`),
  
  // 獲取特定 PDF 的內容
  getPDF: (foldername) => axios.get(`${BASE_URL}/api/reference/${foldername}/pdf`)
}

// 本地儲存 API
export const localStorageAPI = {
  // 儲存設定
  saveSettings: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
      return true
    } catch (error) {
      console.error('儲存設定失敗:', error)
      return false
    }
  },

  // 讀取設定
  loadSettings: (key, defaultValue = null) => {
    try {
      const value = localStorage.getItem(key)
      return value ? JSON.parse(value) : defaultValue
    } catch (error) {
      console.error('讀取設定失敗:', error)
      return defaultValue
    }
  },

  // 刪除設定
  removeSettings: (key) => {
    try {
      localStorage.removeItem(key)
      return true
    } catch (error) {
      console.error('刪除設定失敗:', error)
      return false
    }
  }
}

// 語音相關 API
export const voiceAPI = {
  // 這裡可以添加語音相關的 API
  // 例如：生成語音、獲取語音列表等
} 