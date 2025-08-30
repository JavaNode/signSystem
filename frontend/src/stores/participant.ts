import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { participantsApi } from '@/api/participants'
import type { Participant, CreateParticipantRequest } from '@/api/types'
import { useAppStore } from './app'

export const useParticipantStore = defineStore('participant', () => {
  const appStore = useAppStore()

  // 状态
  const participants = ref<Participant[]>([])
  const currentParticipant = ref<Participant | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 筛选条件
  const filters = ref({
    organization: '',
    group_id: null as number | null,
    is_checked_in: null as boolean | null,
    search: ''
  })

  // 计算属性
  const checkedInParticipants = computed(() => 
    participants.value.filter(p => p.is_checked_in)
  )

  const notCheckedInParticipants = computed(() => 
    participants.value.filter(p => !p.is_checked_in)
  )

  const checkinRate = computed(() => {
    if (participants.value.length === 0) return 0
    return (checkedInParticipants.value.length / participants.value.length) * 100
  })

  const organizationStats = computed(() => {
    const stats = new Map<string, { total: number; checkedIn: number }>()
    
    participants.value.forEach(p => {
      const org = p.organization
      if (!stats.has(org)) {
        stats.set(org, { total: 0, checkedIn: 0 })
      }
      const stat = stats.get(org)!
      stat.total++
      if (p.is_checked_in) {
        stat.checkedIn++
      }
    })

    return Array.from(stats.entries()).map(([org, stat]) => ({
      organization: org,
      total: stat.total,
      checkedIn: stat.checkedIn,
      rate: stat.total > 0 ? (stat.checkedIn / stat.total) * 100 : 0
    }))
  })

  const groupStats = computed(() => {
    const stats = new Map<string, { total: number; checkedIn: number }>()
    
    participants.value.forEach(p => {
      const group = p.group_name || '未分组'
      if (!stats.has(group)) {
        stats.set(group, { total: 0, checkedIn: 0 })
      }
      const stat = stats.get(group)!
      stat.total++
      if (p.is_checked_in) {
        stat.checkedIn++
      }
    })

    return Array.from(stats.entries()).map(([group, stat]) => ({
      group: group,
      total: stat.total,
      checkedIn: stat.checkedIn,
      rate: stat.total > 0 ? (stat.checkedIn / stat.total) * 100 : 0
    }))
  })

  // 方法
  const fetchParticipants = async (params?: {
    page?: number
    size?: number
    organization?: string
    group_id?: number | null
    is_checked_in?: boolean | null
    search?: string
  }) => {
    try {
      loading.value = true
      const response = await participantsApi.getList({
        page: params?.page || currentPage.value,
        size: params?.size || pageSize.value,
        organization: params?.organization || filters.value.organization,
        group_id: params?.group_id !== undefined ? params.group_id : filters.value.group_id,
        is_checked_in: params?.is_checked_in !== undefined ? params.is_checked_in : filters.value.is_checked_in,
        search: params?.search || filters.value.search
      })

      participants.value = response.items
      total.value = response.total
      currentPage.value = response.page
      
      appStore.updateLastUpdateTime()
    } catch (error) {
      console.error('Failed to fetch participants:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取参赛者列表失败',
        message: '请检查网络连接后重试'
      })
    } finally {
      loading.value = false
    }
  }

  const fetchParticipantById = async (id: number) => {
    try {
      loading.value = true
      const participant = await participantsApi.getById(id)
      currentParticipant.value = participant
      return participant
    } catch (error) {
      console.error('Failed to fetch participant:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取参赛者信息失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchParticipantByQrCode = async (qrId: string) => {
    try {
      loading.value = true
      const participant = await participantsApi.getByQrCode(qrId)
      currentParticipant.value = participant
      return participant
    } catch (error) {
      console.error('Failed to fetch participant by QR code:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createParticipant = async (data: CreateParticipantRequest) => {
    try {
      loading.value = true
      const participant = await participantsApi.create(data)
      
      // 添加到列表中
      participants.value.unshift(participant)
      total.value++
      
      appStore.addNotification({
        type: 'success',
        title: '创建成功',
        message: `参赛者 ${participant.name} 创建成功`
      })
      
      return participant
    } catch (error) {
      console.error('Failed to create participant:', error)
      appStore.addNotification({
        type: 'error',
        title: '创建参赛者失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateParticipant = async (id: number, data: Partial<CreateParticipantRequest>) => {
    try {
      loading.value = true
      const participant = await participantsApi.update(id, data)
      
      // 更新列表中的数据
      const index = participants.value.findIndex(p => p.id === id)
      if (index > -1) {
        participants.value[index] = participant
      }
      
      // 更新当前参赛者
      if (currentParticipant.value?.id === id) {
        currentParticipant.value = participant
      }
      
      appStore.addNotification({
        type: 'success',
        title: '更新成功',
        message: `参赛者 ${participant.name} 信息已更新`
      })
      
      return participant
    } catch (error) {
      console.error('Failed to update participant:', error)
      appStore.addNotification({
        type: 'error',
        title: '更新参赛者失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteParticipant = async (id: number) => {
    try {
      loading.value = true
      await participantsApi.delete(id)
      
      // 从列表中移除
      const index = participants.value.findIndex(p => p.id === id)
      if (index > -1) {
        const participant = participants.value[index]
        participants.value.splice(index, 1)
        total.value--
        
        appStore.addNotification({
          type: 'success',
          title: '删除成功',
          message: `参赛者 ${participant.name} 已删除`
        })
      }
      
      // 清除当前参赛者
      if (currentParticipant.value?.id === id) {
        currentParticipant.value = null
      }
    } catch (error) {
      console.error('Failed to delete participant:', error)
      appStore.addNotification({
        type: 'error',
        title: '删除参赛者失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const uploadPhoto = async (id: number, file: File) => {
    try {
      loading.value = true
      const response = await participantsApi.uploadPhoto(id, file)
      
      // 更新参赛者照片路径
      const participant = participants.value.find(p => p.id === id)
      if (participant) {
        participant.photo_path = response.path
      }
      
      if (currentParticipant.value?.id === id) {
        currentParticipant.value.photo_path = response.path
      }
      
      appStore.addNotification({
        type: 'success',
        title: '照片上传成功',
        message: '参赛者照片已更新'
      })
      
      return response
    } catch (error) {
      console.error('Failed to upload photo:', error)
      appStore.addNotification({
        type: 'error',
        title: '照片上传失败',
        message: '请检查文件格式和大小后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const generateQrCode = async (id: number) => {
    try {
      loading.value = true
      const response = await participantsApi.generateQrCode(id)
      
      appStore.addNotification({
        type: 'success',
        title: '二维码生成成功',
        message: '参赛者二维码已生成'
      })
      
      return response
    } catch (error) {
      console.error('Failed to generate QR code:', error)
      appStore.addNotification({
        type: 'error',
        title: '二维码生成失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const generateAllQrCodes = async () => {
    try {
      loading.value = true
      const response = await participantsApi.generateAllQrCodes()
      
      appStore.addNotification({
        type: 'success',
        title: '批量生成成功',
        message: `成功生成 ${response.success_count} 个二维码`
      })
      
      return response
    } catch (error) {
      console.error('Failed to generate all QR codes:', error)
      appStore.addNotification({
        type: 'error',
        title: '批量生成失败',
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
      organization: '',
      group_id: null,
      is_checked_in: null,
      search: ''
    }
  }

  const setCurrentPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
  }

  // 实时更新参赛者签到状态
  const updateParticipantCheckinStatus = (participantId: number, isCheckedIn: boolean, checkinTime?: string) => {
    const participant = participants.value.find(p => p.id === participantId)
    if (participant) {
      participant.is_checked_in = isCheckedIn
      if (checkinTime) {
        participant.checkin_time = checkinTime
      }
    }
    
    if (currentParticipant.value?.id === participantId) {
      currentParticipant.value.is_checked_in = isCheckedIn
      if (checkinTime) {
        currentParticipant.value.checkin_time = checkinTime
      }
    }
  }

  return {
    // 状态
    participants,
    currentParticipant,
    loading,
    total,
    currentPage,
    pageSize,
    filters,

    // 计算属性
    checkedInParticipants,
    notCheckedInParticipants,
    checkinRate,
    organizationStats,
    groupStats,

    // 方法
    fetchParticipants,
    fetchParticipantById,
    fetchParticipantByQrCode,
    createParticipant,
    updateParticipant,
    deleteParticipant,
    uploadPhoto,
    generateQrCode,
    generateAllQrCodes,
    setFilters,
    clearFilters,
    setCurrentPage,
    setPageSize,
    updateParticipantCheckinStatus
  }
})