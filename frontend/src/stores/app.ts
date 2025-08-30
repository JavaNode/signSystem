import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref(false)
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const language = ref('zh-CN')
  const notifications = ref<Array<{
    id: string
    type: 'success' | 'warning' | 'error' | 'info'
    title: string
    message: string
    timestamp: Date
    read: boolean
  }>>([])

  // 系统配置
  const config = ref({
    systemName: '联盟杯内训师大赛管理系统',
    version: '1.0.0',
    apiBaseUrl: '/api',
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif'],
    refreshInterval: 30000, // 30秒
    autoSave: true,
    pageSize: 20
  })

  // 实时数据刷新控制
  const realTimeEnabled = ref(true)
  const lastUpdateTime = ref<Date | null>(null)

  // 计算属性
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.read)
  )

  const unreadCount = computed(() => unreadNotifications.value.length)

  // 方法
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    // 应用主题到document
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  const setLanguage = (lang: string) => {
    language.value = lang
    localStorage.setItem('language', lang)
  }

  const addNotification = (notification: Omit<typeof notifications.value[0], 'id' | 'timestamp' | 'read'>) => {
    const id = Date.now().toString()
    notifications.value.unshift({
      ...notification,
      id,
      timestamp: new Date(),
      read: false
    })

    // 限制通知数量
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }
  }

  const markNotificationAsRead = (id: string) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  const markAllNotificationsAsRead = () => {
    notifications.value.forEach(n => n.read = true)
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAllNotifications = () => {
    notifications.value = []
  }

  const updateConfig = (newConfig: Partial<typeof config.value>) => {
    config.value = { ...config.value, ...newConfig }
    localStorage.setItem('appConfig', JSON.stringify(config.value))
  }

  const setRealTimeEnabled = (enabled: boolean) => {
    realTimeEnabled.value = enabled
    localStorage.setItem('realTimeEnabled', enabled.toString())
  }

  const updateLastUpdateTime = () => {
    lastUpdateTime.value = new Date()
  }

  // 初始化
  const init = () => {
    // 从localStorage恢复设置
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (savedTheme) {
      setTheme(savedTheme)
    }

    const savedLanguage = localStorage.getItem('language')
    if (savedLanguage) {
      language.value = savedLanguage
    }

    const savedConfig = localStorage.getItem('appConfig')
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig)
        config.value = { ...config.value, ...parsedConfig }
      } catch (error) {
        console.error('Failed to parse saved config:', error)
      }
    }

    const savedRealTimeEnabled = localStorage.getItem('realTimeEnabled')
    if (savedRealTimeEnabled !== null) {
      realTimeEnabled.value = savedRealTimeEnabled === 'true'
    }

    // 设置响应式断点监听
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarCollapsed(true)
      }
    }
    window.addEventListener('resize', handleResize)
    handleResize() // 初始检查
  }

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 检查文件类型
  const isValidImageType = (type: string): boolean => {
    return config.value.allowedImageTypes.includes(type)
  }

  // 检查文件大小
  const isValidFileSize = (size: number): boolean => {
    return size <= config.value.maxFileSize
  }

  return {
    // 状态
    loading,
    sidebarCollapsed,
    theme,
    language,
    notifications,
    config,
    realTimeEnabled,
    lastUpdateTime,

    // 计算属性
    unreadNotifications,
    unreadCount,

    // 方法
    setLoading,
    toggleSidebar,
    setSidebarCollapsed,
    setTheme,
    setLanguage,
    addNotification,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    removeNotification,
    clearAllNotifications,
    updateConfig,
    setRealTimeEnabled,
    updateLastUpdateTime,
    init,
    formatFileSize,
    isValidImageType,
    isValidFileSize
  }
})