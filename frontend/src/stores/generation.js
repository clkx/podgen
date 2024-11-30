import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGenerationStore = defineStore('generation', () => {
  // 基礎狀態
  const generationType = ref(null)        // 生成類型：'prompt', 'pdf', 'arxiv'
  const startTime = ref(null)             // 開始時間
  const progress = ref({                  // 進度狀態
    percentage: 0,                        // 當前百分比
    message: '',                          // 當前階段訊息
    stage: 'idle'                         // 當前階段：'idle', 'script', 'audio', 'completed'
  })
  const updateTimer = ref(null)           // 進度更新計時器

  // 估計時間配置（毫秒）
  const timeConfig = {
    prompt: 240000,  // 4分鐘
    pdf: 180000,     // 3分鐘
    arxiv: 180000    // 3分鐘
  }

  // 階段訊息配置
  const stageMessages = {
    prompt: {
      0: '準備開始...',
      20: '分析主題與關鍵字...',
      40: '分析知識庫中的文件...',
      60: '規劃對話架構...',
      80: '生成對話內容...',
      95: '最終調整中...'
    },
    pdf: {
      0: '準備開始...',
      20: '解析 PDF 文件...',
      40: '提取關鍵內容...',
      60: '生成主持人提問...',
      80: '生成專業解說...',
      95: '最終調整中...'
    },
    arxiv: {
      0: '準備開始...',
      20: '獲取論文內容...',
      40: '分析研究方法...',
      60: '生成通俗解說...',
      80: '優化對話流暢度...',
      95: '最終調整中...'
    }
  }

  // 根據百分比獲取階段訊息
  const getMessage = (type, percentage) => {
    const messages = stageMessages[type]
    const stages = Object.keys(messages)
      .map(Number)
      .sort((a, b) => b - a)
    
    for (const stage of stages) {
      if (percentage >= stage) {
        return messages[stage]
      }
    }
    return messages[0]
  }

  // 開始生成
  const startGeneration = (type) => {
    console.log('開始生成，類型:', type)
    
    // 清理之前的狀態
    cleanup()
    
    // 初始化狀態
    generationType.value = type
    startTime.value = Date.now()
    progress.value = {
      percentage: 0,
      message: getMessage(type, 0),
      stage: 'script'
    }

    // 開始定時更新進度
    updateTimer.value = setInterval(() => {
      const elapsed = Date.now() - startTime.value
      const estimatedTime = timeConfig[type]
      
      // 計算新的進度百分比
      let newPercentage = Math.floor((elapsed / estimatedTime) * 100)
      
      // 確保進度不超過99%（除非已完成）
      if (progress.value.stage === 'script') {
        newPercentage = Math.min(newPercentage, 99)
      }
      
      // 更新進度
      if (newPercentage > progress.value.percentage) {
        progress.value = {
          percentage: newPercentage,
          message: getMessage(type, newPercentage),
          stage: progress.value.stage
        }
        console.log('進度更新:', progress.value)
      }
    }, 100)  // 每100ms更新一次
  }

  // 完成腳本生成
  const completeScriptGeneration = () => {
    console.log('腳本生成完成')
    
    // 清理進度更新計時器
    if (updateTimer.value) {
      clearInterval(updateTimer.value)
      updateTimer.value = null
    }

    // 設置完成狀態
    progress.value = {
      percentage: 100,
      message: '腳本生成完成！',
      stage: 'script_completed'
    }
  }

  // 開始音頻生成
  const startAudioGeneration = () => {
    console.log('開始音頻生成')
    progress.value = {
      percentage: 0,
      message: '開始生成語音...',
      stage: 'audio'
    }
  }

  // 更新音頻生成進度
  const updateAudioProgress = (current, total) => {
    const percentage = Math.round((current / total) * 100)
    console.log('音頻生成進度:', percentage)
    
    progress.value = {
      percentage,
      message: `正在生成語音 ${current}/${total} (${percentage}%)`,
      stage: 'audio'
    }
  }

  // 完成所有生成
  const completeGeneration = () => {
    console.log('生成完成')
    cleanup()
    
    progress.value = {
      percentage: 100,
      message: '生成完成！',
      stage: 'completed'
    }
  }

  // 清理函數
  const cleanup = () => {
    if (updateTimer.value) {
      clearInterval(updateTimer.value)
      updateTimer.value = null
    }
  }

  // 計算屬性：是否正在生成中
  const isGenerating = computed(() => {
    return progress.value.stage === 'script' || progress.value.stage === 'audio'
  })

  // 返回 store 的公開介面
  return {
    // 狀態
    progress,
    isGenerating,
    
    // 動作
    startGeneration,
    completeScriptGeneration,
    startAudioGeneration,
    updateAudioProgress,
    completeGeneration,
    cleanup
  }
}) 