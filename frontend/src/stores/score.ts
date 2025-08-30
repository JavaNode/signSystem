import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { scoresApi } from '@/api/scores'
import type { Score, ScoreSubmitRequest, Participant } from '@/api/types'
import { useAppStore } from './app'

export const useScoreStore = defineStore('score', () => {
  const appStore = useAppStore()

  // 状态
  const scores = ref<Score[]>([])
  const currentScore = ref<Score | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const ranking = ref<any[]>([])
  const groupRanking = ref<any[]>([])
  const pendingParticipants = ref<Participant[]>([])

  // 筛选条件
  const filters = ref({
    participant_id: null as number | null,
    judge_id: null as number | null,
    group_id: null as number | null,
    min_score: null as number | null,
    max_score: null as number | null,
    start_time: '',
    end_time: ''
  })

  // 实时统计数据
  const realTimeStats = ref({
    total_scores: 0,
    avg_score: 0,
    max_score: 0,
    min_score: 0,
    participants_scored: 0,
    participants_total: 0,
    scoring_progress: 0,
    recent_scores: [] as Score[],
    score_distribution: [] as any[],
    judge_progress: [] as any[]
  })

  // 计算属性
  const avgScore = computed(() => {
    if (scores.value.length === 0) return 0
    const sum = scores.value.reduce((acc, score) => acc + score.score, 0)
    return Math.round((sum / scores.value.length) * 100) / 100
  })

  const maxScore = computed(() => {
    if (scores.value.length === 0) return 0
    return Math.max(...scores.value.map(s => s.score))
  })

  const minScore = computed(() => {
    if (scores.value.length === 0) return 0
    return Math.min(...scores.value.map(s => s.score))
  })

  const scoreDistribution = computed(() => {
    const distribution = [
      { range: '0-2', count: 0 },
      { range: '2-4', count: 0 },
      { range: '4-6', count: 0 },
      { range: '6-8', count: 0 },
      { range: '8-10', count: 0 }
    ]

    scores.value.forEach(score => {
      if (score.score >= 0 && score.score < 2) distribution[0].count++
      else if (score.score >= 2 && score.score < 4) distribution[1].count++
      else if (score.score >= 4 && score.score < 6) distribution[2].count++
      else if (score.score >= 6 && score.score < 8) distribution[3].count++
      else if (score.score >= 8 && score.score <= 10) distribution[4].count++
    })

    return distribution.map(item => ({
      ...item,
      percentage: scores.value.length > 0 ? (item.count / scores.value.length) * 100 : 0
    }))
  })

  const judgeStats = computed(() => {
    const stats = new Map<string, { count: number; total: number; scores: number[] }>()
    
    scores.value.forEach(score => {
      const judgeName = score.judge_name
      if (!stats.has(judgeName)) {
        stats.set(judgeName, { count: 0, total: 0, scores: [] })
      }
      const stat = stats.get(judgeName)!
      stat.count++
      stat.total += score.score
      stat.scores.push(score.score)
    })

    return Array.from(stats.entries()).map(([judgeName, stat]) => ({
      judge_name: judgeName,
      scores_count: stat.count,
      avg_score: stat.count > 0 ? Math.round((stat.total / stat.count) * 100) / 100 : 0,
      max_score: stat.scores.length > 0 ? Math.max(...stat.scores) : 0,
      min_score: stat.scores.length > 0 ? Math.min(...stat.scores) : 0
    }))
  })

  // 方法
  const fetchScores = async (params?: {
    page?: number
    size?: number
    participant_id?: number | null
    judge_id?: number | null
    group_id?: number | null
    min_score?: number | null
    max_score?: number | null
    start_time?: string
    end_time?: string
  }) => {
    try {
      loading.value = true
      const response = await scoresApi.getList({
        page: params?.page || currentPage.value,
        size: params?.size || pageSize.value,
        participant_id: params?.participant_id !== undefined ? params.participant_id : filters.value.participant_id,
        judge_id: params?.judge_id !== undefined ? params.judge_id : filters.value.judge_id,
        group_id: params?.group_id !== undefined ? params.group_id : filters.value.group_id,
        min_score: params?.min_score !== undefined ? params.min_score : filters.value.min_score,
        max_score: params?.max_score !== undefined ? params.max_score : filters.value.max_score,
        start_time: params?.start_time || filters.value.start_time,
        end_time: params?.end_time || filters.value.end_time
      })

      scores.value = response.items
      total.value = response.total
      currentPage.value = response.page
      
      appStore.updateLastUpdateTime()
    } catch (error) {
      console.error('Failed to fetch scores:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评分列表失败',
        message: '请检查网络连接后重试'
      })
    } finally {
      loading.value = false
    }
  }

  const fetchScoreById = async (id: number) => {
    try {
      loading.value = true
      const score = await scoresApi.getById(id)
      currentScore.value = score
      return score
    } catch (error) {
      console.error('Failed to fetch score:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评分信息失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const submitScore = async (data: ScoreSubmitRequest) => {
    try {
      loading.value = true
      const response = await scoresApi.submit(data)
      
      if (response.success) {
        // 添加到列表中
        scores.value.unshift(response.score)
        total.value++
        
        // 更新实时统计
        await fetchRealTimeStatistics()
        
        appStore.addNotification({
          type: 'success',
          title: '评分成功',
          message: `评分 ${response.score.score} 分已提交`
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to submit score:', error)
      appStore.addNotification({
        type: 'error',
        title: '评分失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateScore = async (id: number, score: number) => {
    try {
      loading.value = true
      const updatedScore = await scoresApi.update(id, score)
      
      // 更新列表中的数据
      const index = scores.value.findIndex(s => s.id === id)
      if (index > -1) {
        scores.value[index] = updatedScore
      }
      
      // 更新当前评分
      if (currentScore.value?.id === id) {
        currentScore.value = updatedScore
      }
      
      appStore.addNotification({
        type: 'success',
        title: '更新成功',
        message: '评分已更新'
      })
      
      return updatedScore
    } catch (error) {
      console.error('Failed to update score:', error)
      appStore.addNotification({
        type: 'error',
        title: '更新评分失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteScore = async (id: number) => {
    try {
      loading.value = true
      await scoresApi.delete(id)
      
      // 从列表中移除
      const index = scores.value.findIndex(s => s.id === id)
      if (index > -1) {
        scores.value.splice(index, 1)
        total.value--
        
        appStore.addNotification({
          type: 'success',
          title: '删除成功',
          message: '评分已删除'
        })
      }
      
      // 清除当前评分
      if (currentScore.value?.id === id) {
        currentScore.value = null
      }
    } catch (error) {
      console.error('Failed to delete score:', error)
      appStore.addNotification({
        type: 'error',
        title: '删除评分失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchParticipantScores = async (participantId: number) => {
    try {
      loading.value = true
      const response = await scoresApi.getParticipantScores(participantId)
      return response
    } catch (error) {
      console.error('Failed to fetch participant scores:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取参赛者评分失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchJudgeScores = async (judgeId: number, params?: {
    page?: number
    size?: number
    participant_id?: number
  }) => {
    try {
      loading.value = true
      const response = await scoresApi.getJudgeScores(judgeId, params)
      return response
    } catch (error) {
      console.error('Failed to fetch judge scores:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评委评分失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchRealTimeStatistics = async () => {
    try {
      const stats = await scoresApi.getRealTimeStatistics()
      realTimeStats.value = stats
      appStore.updateLastUpdateTime()
      return stats
    } catch (error) {
      console.error('Failed to fetch real-time statistics:', error)
      throw error
    }
  }

  const fetchRanking = async (params?: {
    group_id?: number
    limit?: number
  }) => {
    try {
      loading.value = true
      const response = await scoresApi.getRanking(params)
      ranking.value = response
      return response
    } catch (error) {
      console.error('Failed to fetch ranking:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取排行榜失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchGroupRanking = async () => {
    try {
      loading.value = true
      const response = await scoresApi.getGroupRanking()
      groupRanking.value = response
      return response
    } catch (error) {
      console.error('Failed to fetch group ranking:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取分组排行榜失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchPendingParticipants = async (judgeId?: number) => {
    try {
      loading.value = true
      const participants = await scoresApi.getPendingParticipants(judgeId)
      pendingParticipants.value = participants
      return participants
    } catch (error) {
      console.error('Failed to fetch pending participants:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取待评分参赛者失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const batchSubmitScores = async (scoresData: Array<{
    participant_id: number
    score: number
  }>) => {
    try {
      loading.value = true
      const response = await scoresApi.batchSubmit({ scores: scoresData })
      
      // 刷新评分列表
      await fetchScores()
      
      appStore.addNotification({
        type: 'success',
        title: '批量评分成功',
        message: `成功提交 ${response.success_count} 个评分`
      })
      
      if (response.error_count > 0) {
        appStore.addNotification({
          type: 'warning',
          title: '部分评分失败',
          message: `${response.error_count} 个评分提交失败`
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to batch submit scores:', error)
      appStore.addNotification({
        type: 'error',
        title: '批量评分失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const setFilters = (newFilters: Partial<typeof filters.value>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      participant_id: null,
      judge_id: null,
      group_id: null,
      min_score: null,
      max_score: null,
      start_time: '',
      end_time: ''
    }
  }

  const setCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
  }

  const clearCurrentScore = () => {
    currentScore.value = null
  }

  // 实时更新评分数据
  const addNewScore = (score: Score) => {
    scores.value.unshift(score)
    total.value++
    
    // 更新实时统计
    realTimeStats.value.total_scores++
    realTimeStats.value.recent_scores.unshift(score)
    if (realTimeStats.value.recent_scores.length > 10) {
      realTimeStats.value.recent_scores = realTimeStats.value.recent_scores.slice(0, 10)
    }
  }

  return {
    // 状态
    scores,
    currentScore,
    loading,
    total,
    currentPage,
    pageSize,
    ranking,
    groupRanking,
    pendingParticipants,
    filters,
    realTimeStats,

    // 计算属性
    avgScore,
    maxScore,
    minScore,
    scoreDistribution,
    judgeStats,

    // 方法
    fetchScores,
    fetchScoreById,
    submitScore,
    updateScore,
    deleteScore,
    fetchParticipantScores,
    fetchJudgeScores,
    fetchRealTimeStatistics,
    fetchRanking,
    fetchGroupRanking,
    fetchPendingParticipants,
    batchSubmitScores,
    setFilters,
    clearFilters,
    setCurrentPage,
    setPageSize,
    clearCurrentScore,
    addNewScore
  }
})