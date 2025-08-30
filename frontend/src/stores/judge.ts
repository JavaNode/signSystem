import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { judgesApi } from '@/api/judges'
import type { Judge, CreateJudgeRequest } from '@/api/types'
import { useAppStore } from './app'

export const useJudgeStore = defineStore('judge', () => {
  const appStore = useAppStore()

  // 状态
  const judges = ref<Judge[]>([])
  const currentJudge = ref<Judge | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 筛选条件
  const filters = ref({
    organization: '',
    is_active: null as boolean | null,
    search: ''
  })

  // 计算属性
  const activeJudges = computed(() => 
    judges.value.filter(j => j.is_active)
  )

  const inactiveJudges = computed(() => 
    judges.value.filter(j => !j.is_active)
  )

  const organizationStats = computed(() => {
    const stats = new Map<string, { total: number; active: number }>()
    
    judges.value.forEach(j => {
      const org = j.organization
      if (!stats.has(org)) {
        stats.set(org, { total: 0, active: 0 })
      }
      const stat = stats.get(org)!
      stat.total++
      if (j.is_active) {
        stat.active++
      }
    })

    return Array.from(stats.entries()).map(([org, stat]) => ({
      organization: org,
      total: stat.total,
      active: stat.active,
      rate: stat.total > 0 ? (stat.active / stat.total) * 100 : 0
    }))
  })

  // 方法
  const fetchJudges = async (params?: {
    page?: number
    size?: number
    organization?: string
    is_active?: boolean | null
    search?: string
  }) => {
    try {
      loading.value = true
      const response = await judgesApi.getList({
        page: params?.page || currentPage.value,
        size: params?.size || pageSize.value,
        organization: params?.organization || filters.value.organization,
        is_active: params?.is_active !== undefined ? params.is_active : filters.value.is_active,
        search: params?.search || filters.value.search
      })

      judges.value = response.items
      total.value = response.total
      currentPage.value = response.page
      
      appStore.updateLastUpdateTime()
    } catch (error) {
      console.error('Failed to fetch judges:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评委列表失败',
        message: '请检查网络连接后重试'
      })
    } finally {
      loading.value = false
    }
  }

  const fetchJudgeById = async (id: number) => {
    try {
      loading.value = true
      const judge = await judgesApi.getById(id)
      currentJudge.value = judge
      return judge
    } catch (error) {
      console.error('Failed to fetch judge:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评委信息失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const createJudge = async (data: CreateJudgeRequest) => {
    try {
      loading.value = true
      const judge = await judgesApi.create(data)
      
      // 添加到列表中
      judges.value.unshift(judge)
      total.value++
      
      appStore.addNotification({
        type: 'success',
        title: '创建成功',
        message: `评委 ${judge.name} 创建成功`
      })
      
      return judge
    } catch (error) {
      console.error('Failed to create judge:', error)
      appStore.addNotification({
        type: 'error',
        title: '创建评委失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateJudge = async (id: number, data: Partial<Omit<CreateJudgeRequest, 'password'>>) => {
    try {
      loading.value = true
      const judge = await judgesApi.update(id, data)
      
      // 更新列表中的数据
      const index = judges.value.findIndex(j => j.id === id)
      if (index > -1) {
        judges.value[index] = judge
      }
      
      // 更新当前评委
      if (currentJudge.value?.id === id) {
        currentJudge.value = judge
      }
      
      appStore.addNotification({
        type: 'success',
        title: '更新成功',
        message: `评委 ${judge.name} 信息已更新`
      })
      
      return judge
    } catch (error) {
      console.error('Failed to update judge:', error)
      appStore.addNotification({
        type: 'error',
        title: '更新评委失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const resetPassword = async (id: number, newPassword: string) => {
    try {
      loading.value = true
      await judgesApi.resetPassword(id, newPassword)
      
      appStore.addNotification({
        type: 'success',
        title: '密码重置成功',
        message: '评委密码已重置'
      })
    } catch (error) {
      console.error('Failed to reset password:', error)
      appStore.addNotification({
        type: 'error',
        title: '密码重置失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const toggleActive = async (id: number, isActive: boolean) => {
    try {
      loading.value = true
      await judgesApi.toggleActive(id, isActive)
      
      // 更新列表中的状态
      const judge = judges.value.find(j => j.id === id)
      if (judge) {
        judge.is_active = isActive
      }
      
      // 更新当前评委
      if (currentJudge.value?.id === id) {
        currentJudge.value.is_active = isActive
      }
      
      appStore.addNotification({
        type: 'success',
        title: isActive ? '启用成功' : '禁用成功',
        message: `评委已${isActive ? '启用' : '禁用'}`
      })
    } catch (error) {
      console.error('Failed to toggle judge active status:', error)
      appStore.addNotification({
        type: 'error',
        title: '操作失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteJudge = async (id: number) => {
    try {
      loading.value = true
      await judgesApi.delete(id)
      
      // 从列表中移除
      const index = judges.value.findIndex(j => j.id === id)
      if (index > -1) {
        const judge = judges.value[index]
        judges.value.splice(index, 1)
        total.value--
        
        appStore.addNotification({
          type: 'success',
          title: '删除成功',
          message: `评委 ${judge.name} 已删除`
        })
      }
      
      // 清除当前评委
      if (currentJudge.value?.id === id) {
        currentJudge.value = null
      }
    } catch (error) {
      console.error('Failed to delete judge:', error)
      appStore.addNotification({
        type: 'error',
        title: '删除评委失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const checkUsername = async (username: string, excludeId?: number) => {
    try {
      const response = await judgesApi.checkUsername(username, excludeId)
      return response.available
    } catch (error) {
      console.error('Failed to check username:', error)
      return false
    }
  }

  const fetchScoringProgress = async (judgeId?: number) => {
    try {
      loading.value = true
      const progress = await judgesApi.getScoringProgress(judgeId)
      return progress
    } catch (error) {
      console.error('Failed to fetch scoring progress:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取评分进度失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const batchResetPassword = async (judgeIds: number[], newPassword: string) => {
    try {
      loading.value = true
      const response = await judgesApi.batchResetPassword(judgeIds, newPassword)
      
      appStore.addNotification({
        type: 'success',
        title: '批量重置成功',
        message: `成功重置 ${response.success_count} 个评委密码`
      })
      
      if (response.error_count > 0) {
        appStore.addNotification({
          type: 'warning',
          title: '部分重置失败',
          message: `${response.error_count} 个评委密码重置失败`
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to batch reset password:', error)
      appStore.addNotification({
        type: 'error',
        title: '批量重置失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const importJudges = async (judgesData: Array<{
    name: string
    username: string
    password: string
    organization: string
  }>) => {
    try {
      loading.value = true
      const response = await judgesApi.import({ judges: judgesData })
      
      // 刷新列表
      await fetchJudges()
      
      appStore.addNotification({
        type: 'success',
        title: '导入成功',
        message: `成功导入 ${response.success_count} 个评委`
      })
      
      if (response.error_count > 0) {
        appStore.addNotification({
          type: 'warning',
          title: '部分导入失败',
          message: `${response.error_count} 个评委导入失败`
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to import judges:', error)
      appStore.addNotification({
        type: 'error',
        title: '导入失败',
        message: '请检查数据格式后重试'
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
      organization: '',
      is_active: null,
      search: ''
    }
  }

  const setCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
  }

  const clearCurrentJudge = () => {
    currentJudge.value = null
  }

  return {
    // 状态
    judges,
    currentJudge,
    loading,
    total,
    currentPage,
    pageSize,
    filters,

    // 计算属性
    activeJudges,
    inactiveJudges,
    organizationStats,

    // 方法
    fetchJudges,
    fetchJudgeById,
    createJudge,
    updateJudge,
    resetPassword,
    toggleActive,
    deleteJudge,
    checkUsername,
    fetchScoringProgress,
    batchResetPassword,
    importJudges,
    setFilters,
    clearFilters,
    setCurrentPage,
    setPageSize,
    clearCurrentJudge
  }
})