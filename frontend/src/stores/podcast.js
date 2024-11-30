// stores/podcast.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useCharacterStore } from './character'
import { useGenerationStore } from './generation'
import { Howl } from 'howler'

export const usePodcastStore = defineStore('podcast', () => {
  // 取得其他 store
  const characterStore = useCharacterStore()
  const generationStore = useGenerationStore()

  // 狀態
  const script = ref(null)
  const audioQueue = ref([])
  const generationStatus = ref('idle')
  const currentProgress = ref({
    stage: null,
    percentage: 0,
    message: ''
  })
  const error = ref(null)

  // 音頻播放相關狀態
  const isPlaying = ref(false)
  const currentAudioIndex = ref(0)
  let currentSound = null

  // 添加生成完成的狀態
  const showProgress = ref(false)  // 改為預設不顯示
  const fadeOutProgress = ref(false)

  // Actions
  const generateFromArxiv = async (arxivUrl) => {
    try {
      // 開始生成時顯示進度
      showProgress.value = true
      fadeOutProgress.value = false
      
      error.value = null
      generationStatus.value = 'generating-script'
      currentProgress.value = {
        stage: 'script',
        percentage: 0,
        message: '正在生成對話腳本'
      }

      console.log('開始從 arXiv 生成 Podcast:', arxivUrl)
      const scriptResult = await generateScript(arxivUrl)
      
      // 2. 生成語音
      currentProgress.value = {
        stage: 'audio',
        percentage: 0,
        message: '正在生成語音...'
      }
      generationStatus.value = 'generating-audio'
      
      // 清空之前的音頻佇列
      audioQueue.value = []
      currentAudioIndex.value = 0
      
      await generateAudio(scriptResult)
      
      // 生成完成後，延遲一下再淡出進度區域
      fadeOutProgress.value = true
      setTimeout(() => {
        showProgress.value = false
      }, 1000)  // 1秒後隱藏

      generationStatus.value = 'completed'
    } catch (err) {
      console.error('Podcast 生成失敗:', {
        error: err,
        message: err.message,
        stack: err.stack,
        name: err.name
      })
      error.value = err instanceof Error ? err.message : '生成失敗：' + JSON.stringify(err)
      generationStatus.value = 'error'
      throw err instanceof Error ? err : new Error(JSON.stringify(err))
    }
  }

  const generateScript = async (arxivUrl) => {
    try {
      console.log('開始生成腳本，參數:', {
        arxivUrl,
        host: characterStore.host,
        guest: characterStore.guest
      })
      
      // 確保背景資料存在
      if (!characterStore.host.background || !characterStore.guest.background) {
        throw new Error('請先設定主持人和來賓的背景資料')
      }
      
      // 調用後端 API 生成腳本
      const response = await fetch('http://localhost:8000/api/generate/script/arxiv', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          arxiv_url: arxivUrl,
          host_name: characterStore.host.name,
          host_background: characterStore.host.background,  // 確保這個值存在
          guest_name: characterStore.guest.name,
          guest_background: characterStore.guest.background  // 確保這個值存在
        })
      })

      const responseData = await response.json()
      console.log('API 回應內容:', JSON.stringify(responseData, null, 2))

      if (!response.ok) {
        if (responseData.detail) {
          // 如果是驗證錯誤，提供更友好的錯誤訊息
          if (Array.isArray(responseData.detail)) {
            const errors = responseData.detail.map(err => {
              if (err.loc.includes('host_background')) {
                return '請設定主持人背景'
              }
              if (err.loc.includes('guest_background')) {
                return '請設定來賓背景'
              }
              return err.msg
            })
            throw new Error(errors.join('\n'))
          }
          throw new Error(responseData.detail)
        }
        throw new Error('生成腳本失敗')
      }

      // 驗證回應格式
      if (!responseData.dialogue || !Array.isArray(responseData.dialogue)) {
        console.error('回應格式錯誤:', responseData)
        throw new Error('API 回應格式不正確')
      }

      // 更新腳本狀態
      script.value = responseData
      return responseData

    } catch (err) {
      // 詳細記錄錯誤信息
      console.error('腳本生成失敗:', {
        error: err,
        message: err.message,
        name: err.name,
        stack: err.stack,
        toString: err.toString()
      })
      
      // 確保拋出的是字符串錯誤消息
      const errorMessage = err.message || '腳本生成失敗'
      throw new Error(errorMessage)
    }
  }

  const generateAudio = async (scriptData) => {
    try {
      console.log('開始生成語音，原始資料:', scriptData)
      
      // 驗證必要的資料
      if (!scriptData || !scriptData.dialogue || !Array.isArray(scriptData.dialogue)) {
        throw new Error('無效的腳本資料格式')
      }

      // 確保 dialogue 格式正確
      const formattedDialogue = scriptData.dialogue.map((line, index) => {
        if (!line.speaker || !line.content) {
          throw new Error(`對話行 ${index + 1} 缺少必要資料`)
        }
        return {
          speaker: line.speaker,
          content: line.content,
          speaker_type: line.speaker === scriptData.host_name ? 'host' : 'guest'
        }
      })

      console.log('格式化後的對話資料:', formattedDialogue)

      // 驗證角色設定
      if (!characterStore.host.name || !characterStore.guest.name) {
        throw new Error('請先設定主持人和來賓的名稱')
      }

      const requestData = {
        script: {
          dialogue: formattedDialogue,
          host_name: characterStore.host.name,
          guest_name: characterStore.guest.name,
          host_background: characterStore.host.background,
          guest_background: characterStore.guest.background
        },
        voice_settings: {
          host_voice: characterStore.host.voice || "zh-TW-HsiaoChenNeural",
          guest_voice: characterStore.guest.voice || "zh-TW-YunJheNeural"
        }
      }

      console.log('發送請求資料:', requestData)

      const response = await fetch('http://localhost:8000/api/synthesize/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        console.error('語音生成請求失敗:', errorData)
        
        // 處理驗證錯誤
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => {
            // 解析錯誤位置和訊息
            const location = err.loc.join('.')
            return `${location}: ${err.msg}`
          })
          throw new Error('資料驗證錯誤：\n' + errorMessages.join('\n'))
        }
        
        throw new Error(errorData.detail || '語音生成失敗')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        
        // 處理完整的 JSON 物件
        while (buffer.includes('\n')) {
          const newlineIndex = buffer.indexOf('\n')
          const jsonString = buffer.slice(0, newlineIndex)
          buffer = buffer.slice(newlineIndex + 1)

          try {
            const segment = JSON.parse(jsonString)
            await handleAudioSegment(segment)
          } catch (err) {
            console.error('解析音頻段落失敗:', err)
            throw new Error('音頻段落處理失敗：' + err.message)
          }
        }
      }
    } catch (error) {
      console.error('語音生成失敗:', error)
      throw error
    }
  }

  const handleAudioSegment = async (segment) => {
    console.log('收到音頻段落:', segment)
    
    if (segment.type === 'audio' && segment.status === 'success') {
      // 更新進度
      generationStore.updateAudioProgress(segment.index + 1, segment.total)
      
      // 將音頻段落加入佇列
      const audioData = {
        index: segment.index,
        content: segment.content,
        audioFile: segment.audio_file,  // 改回使用 audio_file
        speaker: segment.speaker
      }
      
      // 確保按照順序插入
      if (!audioQueue.value[segment.index]) {
        audioQueue.value[segment.index] = audioData
      }
      
      console.log('當前佇列:', audioQueue.value)
    }
  }

  // 播放控制相關方法
  const playNextSegment = () => {
    console.log('開始播放下一段', {
        currentIndex: currentAudioIndex.value,
        queueLength: audioQueue.value.length,
        currentSound: !!currentSound,
        segment: audioQueue.value[currentAudioIndex.value]
    })

    // 檢查是否已經播放完所有段落
    if (currentAudioIndex.value >= audioQueue.value.length) {
        console.log('所有段落播放完畢')
        isPlaying.value = false
        currentAudioIndex.value = 0  // 重置為第一段
        return
    }

    // 檢查音頻檔案是否存在
    const segment = audioQueue.value[currentAudioIndex.value]
    if (!segment?.audioFile) {
        console.error('無效的音頻檔案路徑')
        return
    }

    // 構建完整的音頻 URL
    const audioUrl = new URL(segment.audioFile, 'http://localhost:8000').href
    console.log('完整音頻 URL:', audioUrl)

    // 創建音頻播放器
    currentSound = new Howl({
        src: [audioUrl],
        html5: true,
        format: ['wav'],
        preload: true,
        onload: () => {
            console.log('音頻載入成功，開始播放')
            currentSound.play()
        },
        onplay: () => {
            console.log('開始播放段落:', currentAudioIndex.value)
            isPlaying.value = true
        },
        onpause: () => {
            console.log('暫停播放')
            isPlaying.value = false
        },
        onend: () => {
            console.log('播放結束')
            if (currentAudioIndex.value < audioQueue.value.length - 1) {
                currentAudioIndex.value++
                playNextSegment()
            } else {
                console.log('播放完畢')
                isPlaying.value = false
                currentAudioIndex.value = 0
            }
        }
    })
  }

  const togglePlay = () => {
    console.log('切換播放狀態', {
        isPlaying: isPlaying.value,
        currentSound: !!currentSound,
        currentIndex: currentAudioIndex.value,
        queueLength: audioQueue.value.length
    })
    
    if (!currentSound) {
        if (audioQueue.value.length > 0) {
            console.log('開始新的播放')
            playNextSegment()
        } else {
            console.log('沒有可播放的音頻')
        }
        return
    }

    if (isPlaying.value) {
        console.log('暫停播放')
        currentSound.pause()
    } else {
        console.log('繼續播放')
        currentSound.play()
    }
  }

  const stop = () => {
    if (currentSound) {
      currentSound.stop()
      currentAudioIndex.value = 0
    }
  }

  // 添加跳轉方法
  const seekTo = (index) => {
    if (index < 0 || index >= audioQueue.value.length) return
    
    // 停止當前播放
    if (currentSound) {
      currentSound.stop()
      currentSound.unload()
      currentSound = null
    }
    
    // 設置新的索引
    currentAudioIndex.value = index
    
    // 開始播放新的段落
    playNextSegment()
  }

  // 添加新的 action
  const generateFromPrompt = async (topic) => {
    try {
      // 開始生成腳本
      showProgress.value = true
      fadeOutProgress.value = false
      error.value = null
      generationStatus.value = 'generating-script'

      // 準備請求資料
      const requestData = {
        topic: topic,
        max_analysts: 3,
        host_name: characterStore.host.name,
        host_background: characterStore.host.background,
        guest_name: characterStore.guest.name,
        guest_background: characterStore.guest.background
      }

      // 調用後端 API 生成腳本
      const response = await fetch('http://localhost:8000/api/generate/script/prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      const responseData = await response.json()
      
      if (!response.ok) {
        if (responseData.detail) {
          throw new Error(typeof responseData.detail === 'string' 
            ? responseData.detail 
            : JSON.stringify(responseData.detail))
        }
        throw new Error('生成腳本失敗')
      }

      // 更新腳本狀態
      script.value = responseData

      // 開始生成語音
      generationStatus.value = 'generating-audio'
      
      // 清空之前的音頻佇列
      audioQueue.value = []
      currentAudioIndex.value = 0
      
      // 生成語音
      await generateAudio(responseData)
      
      // 生成完成後，延遲一下再淡出進度區域
      fadeOutProgress.value = true
      setTimeout(() => {
        showProgress.value = false
      }, 1000)

      generationStatus.value = 'completed'
      
      return responseData
    } catch (error) {
      console.error('Prompt 生成失敗:', error)
      generationStatus.value = 'error'
      throw error
    }
  }

  const generateFromPDF = async (pdfFile) => {
    try {
      // 開始生成時顯示進度
      showProgress.value = true
      fadeOutProgress.value = false
      
      error.value = null
      generationStatus.value = 'generating-script'
      currentProgress.value = {
        stage: 'script',
        percentage: 0,
        message: '正在生成對話腳本'
      }

      // 建立 FormData，確保所有必要欄位都有值
      const formData = new FormData()
      formData.append('pdf_file', pdfFile)  // 檔案必須是 File 物件
      formData.append('host_name', characterStore.host.name || '')
      formData.append('host_background', characterStore.host.background || '')
      formData.append('guest_name', characterStore.guest.name || '')
      formData.append('guest_background', characterStore.guest.background || '')

      // 調用後端 API 生成腳本
      const response = await fetch('http://localhost:8000/api/generate/script/pdf', {
        method: 'POST',
        body: formData
      })

      const responseData = await response.json()
      console.log('API 回應內容:', JSON.stringify(responseData, null, 2))

      if (!response.ok) {
        if (responseData.detail) {
          // 處理驗證錯誤
          if (Array.isArray(responseData.detail)) {
            const errors = responseData.detail.map(err => {
              switch (err.loc[1]) {
                case 'host_name':
                  return '請設定主持人名稱'
                case 'host_background':
                  return '設定主持人背景'
                case 'guest_name':
                  return '請設定來賓名稱'
                case 'guest_background':
                  return '請設定來賓背景'
                default:
                  return err.msg
              }
            })
            throw new Error(errors.join('\n'))
          }
          throw new Error(responseData.detail)
        }
        throw new Error('PDF 腳本生成失敗')
      }

      // 更新腳本狀態
      script.value = responseData

      // 生成語音
      currentProgress.value = {
        stage: 'audio',
        percentage: 0,
        message: '正在生成語音...'
      }
      generationStatus.value = 'generating-audio'
      
      // 清空之前的音頻佇列
      audioQueue.value = []
      currentAudioIndex.value = 0
      
      await generateAudio(responseData)
      
      // 生成完成後，延遲一下再淡出進度區域
      fadeOutProgress.value = true
      setTimeout(() => {
        showProgress.value = false
      }, 1000)

      generationStatus.value = 'completed'
    } catch (err) {
      console.error('PDF 生成失敗:', {
        error: err,
        message: err.message,
        stack: err.stack
      })
      error.value = err.message || 'PDF 生成失敗'
      generationStatus.value = 'error'
      throw err
    }
  }

  // Getters
  const isGenerating = computed(() => {
    return generationStatus.value === 'generating-script' || 
           generationStatus.value === 'generating-audio'
  })

  const progress = computed(() => {
    return {
      ...currentProgress.value,
      isGenerating: isGenerating.value
    }
  })

  return {
    // State
    script,
    audioQueue,
    generationStatus,
    currentProgress,
    error,
    isPlaying,
    currentAudioIndex,

    // Getters
    isGenerating,
    progress,

    // Actions
    generateFromArxiv,
    generateScript,
    generateAudio,
    togglePlay,
    stop,
    playNextSegment,
    seekTo,
    showProgress,
    fadeOutProgress,
    generateFromPrompt,
    generateFromPDF
  }
})