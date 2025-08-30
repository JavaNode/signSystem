import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statisticsApi } from '@/api/statistics'
import type { Statistics } from '@/api/types'
import { useAppStore } from './app'

export const useStatisticsStore = defineStore('statistics', () => {
  const appStore = useAppStore()

  // 状态
  const overview = ref<Statistics | null>(null)
  const realTimeData = ref<any>(null)
  const checkinStats = ref<any>(null)
  const scoreStats = ref<any>(null)
  const groupStats = ref<any>(null)
  const judgeStats = ref<any>(null)
  const trends = ref<any>(null)
  const comparison = ref<any>(null)
  const loading = ref(false)
  const lastUpdateTime = ref<Date | null>(null)

  // 计算属性
  const checkinRate = computed(() => {
    if (!overview.value) return 0
    return overview.value.checkin_rate || 0
  })

  const avgScore = computed(() => {
    if (!overview.value) return 0
    return overview.value.avg_score || 0
  })

  const totalParticipants = computed(() => {
    if (!overview.value) return 0
    return overview.value.total_participants || 0
  })

  const checkedInCount = computed(() => {
    if (!overview.value) return 0
    return overview.value.checked_in_count || 0
  })

  const totalGroups = computed(() => {
    if (!overview.value) return 0
    return overview.value.total_groups || 0
  })

  const totalJudges = computed(() => {
    if (!overview.value) return 0
    return overview.value.total_judges || 0
  })

  const totalScores = computed(() => {
    if (!overview.value) return 0
    return overview.value.total_scores || 0
  })

  const organizationPerformance = computed(() => {
    if (!overview.value?.checkin_by_organization) return []
    return overview.value.checkin_by_organization.sort((a, b) => b.rate - a.rate)
  })

  const checkinTimeline = computed(() => {
    if (!overview.value?.checkin_timeline) return []
    return overview.value.checkin_timeline
  })

  const scoreDistribution = computed(() => {
    if (!overview.value?.score_distribution) return []
    return overview.value.score_distribution
  })

  // 方法
  const fetchOverview = async () => {
    try {
      loading.value = true
      const data = await statisticsApi.getOverview()
      overview.value = data
      lastUpdateTime.value = new Date()
      appStore.updateLastUpdateTime()
    } catch (error) {
      console.error('Failed to fetch overview statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取统计概览失败',
        message: '请检查网络连接后重试'
      })
    } finally {
      loading.value = false
    }
  }

  const fetchRealTimeData = async () => {
    try {
      const data = await statisticsApi.getRealTime()
      realTimeData.value = data
      lastUpdateTime.value = new Date()
      appStore.updateLastUpdateTime()
      return data
    } catch (error) {
      console.error('Failed to fetch real-time data:', error)
      throw error
    }
  }

  const fetchCheckinStats = async (params?: {
    start_time?: string
    end_time?: string
    group_by?: 'hour' | 'organization' | 'group'
  }) => {
    try {
      loading.value = true
      const data = await statisticsApi.getCheckinStats(params)
      checkinStats.value = data
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch checkin statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取签到统计失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchScoreStats = async (params?: {
    start_time?: string
    end_time?: string
    group_by?: 'judge' | 'organization' | 'group' | 'score_range'
  }) => {
    try {
      loading.value = true
      const data = await statisticsApi.getScoreStats(params)
      scoreStats.value = data
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch score statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评分统计失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchGroupStats = async () => {
    try {
      loading.value = true
      const data = await statisticsApi.getGroupStats()
      groupStats.value = data
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch group statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取分组统计失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchJudgeStats = async () => {
    try {
      loading.value = true
      const data = await statisticsApi.getJudgeStats()
      judgeStats.value = data
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch judge statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评委统计失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchTrends = async (params?: {
    period?: 'hour' | 'day' | 'week'
    start_time?: string
    end_time?: string
  }) => {
    try {
      loading.value = true
      const data = await statisticsApi.getTrends(params)
      trends.value = data
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch trends:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取趋势分析失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchComparison = async (params?: {
    compare_by?: 'organization' | 'group' | 'judge'
    metric?: 'checkin_rate' | 'avg_score' | 'participation'
  }) => {
    try {
      loading.value = true
      const data = await statisticsApi.getComparison(params)
      comparison.value = data
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch comparison:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取比较分析失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchSystemStats = async () => {
    try {
      const data = await statisticsApi.getSystemStats()
      return data
    } catch (error) {
      console.error('Failed to fetch system statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取系统统计失败',
        message: '请检查网络连接后重试'
      })
      throw error
    }
  }

  const fetchActivityStats = async (params?: {
    start_time?: string
    end_time?: string
    activity_type?: 'checkin' | 'score' | 'login' | 'all'
  }) => {
    try {
      loading.value = true
      const data = await statisticsApi.getActivityStats(params)
      lastUpdateTime.value = new Date()
      return data
    } catch (error) {
      console.error('Failed to fetch activity statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取活动统计失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const exportReport = async (params?: {
    report_type?: 'overview' | 'checkin' | 'scores' | 'groups' | 'judges' | 'complete'
    format?: 'excel' | 'pdf' | 'csv'
    include_charts?: boolean
    start_time?: string
    end_time?: string
  }) => {
    try {
      loading.value = true
      const blob = await statisticsApi.exportReport(params)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // 设置文件名
      const format = params?.format || 'excel'
      const reportType = params?.report_type || 'overview'
      const timestamp = new Date().toISOString().slice(0, 10)
      link.download = `统计报告_${reportType}_${timestamp}.${format === 'excel' ? 'xlsx' : format}`
      
      // 触发下载
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      appStore.addNotification({
        type: 'success',
        title: '导出成功',
        message: '统计报告已下载'
      })
    } catch (error) {
      console.error('Failed to export report:', error)
      appStore.addNotification({
        type: 'error',
        title: '导出失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  // 刷新所有统计数据
  const refreshAllStats = async () => {
    try {
      loading.value = true
      await Promise.all([
        fetchOverview(),
        fetchRealTimeData(),
        fetchCheckinStats(),
        fetchScoreStats(),
        fetchGroupStats(),
        fetchJudgeStats()
      ])
      
      appStore.addNotification({
        type: 'success',
        title: '刷新成功',
        message: '所有统计数据已更新'
      })
    } catch (error) {
      console.error('Failed to refresh all statistics:', error)
      appStore.addNotification({
        type: 'error',
        title: '刷新失败',
        message: '部分数据更新失败，请稍后重试'
      })
    } finally {
      loading.value = false
    }
  }

  // 清除所有缓存数据
  const clearAllData = () => {
    overview.value = null
    realTimeData.value = null
    checkinStats.value = null
    scoreStats.value = null
    groupStats.value = null
    judgeStats.value = null
    trends.value = null
    comparison.value = null
    lastUpdateTime.value = null
  }

  // 获取数据更新状态
  const getUpdateStatus = () => {
    if (!lastUpdateTime.value) return '未更新'
    
    const now = new Date()
    const diff = now.getTime() - lastUpdateTime.value.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return '刚刚更新'
    if (minutes < 60) return `${minutes}分钟前更新`
    
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}小时前更新`
    
    const days = Math.floor(hours / 24)
    return `${days}天前更新`
  }

  // 检查数据是否需要刷新
  const needsRefresh = (maxAgeMinutes: number = 5) => {
    if (!lastUpdateTime.value) return true
    
    const now = new Date()
    const diff = now.getTime() - lastUpdateTime.value.getTime()
    const minutes = Math.floor(diff / 60000)
    
    return minutes >= maxAgeMinutes
  }

  return {
    // 状态
    overview,
    realTimeData,
    checkinStats,
    scoreStats,
    groupStats,
    judgeStats,
    trends,
    comparison,
    loading,
    lastUpdateTime,

    // 计算属性
    checkinRate,
    avgScore,
    totalParticipants,
    checkedInCount,
    totalGroups,
    totalJudges,
    totalScores,
    organizationPerformance,
    checkinTimeline,
    scoreDistribution,

    // 方法
    fetchOverview,
    fetchRealTimeData,
    fetchCheckinStats,
    fetchScoreStats,
    fetchGroupStats,
    fetchJudgeStats,
    fetchTrends,
    fetchComparison,
    fetchSystemStats,
    fetchActivityStats,
    exportReport,
    refreshAllStats,
    clearAllData,
    getUpdateStatus,
    needsRefresh
  }
})