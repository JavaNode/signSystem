import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { groupsApi } from '@/api/groups'
import type { Group, CreateGroupRequest, Participant } from '@/api/types'
import { useAppStore } from './app'

export const useGroupStore = defineStore('group', () => {
  const appStore = useAppStore()

  // 状态
  const groups = ref<Group[]>([])
  const currentGroup = ref<Group | null>(null)
  const currentGroupMembers = ref<Participant[]>([])
  const loading = ref(false)
  const availableParticipants = ref<Participant[]>([])

  // 计算属性
  const totalGroups = computed(() => groups.value.length)

  const totalMembers = computed(() => 
    groups.value.reduce((sum, group) => sum + group.member_count, 0)
  )

  const avgMembersPerGroup = computed(() => {
    if (totalGroups.value === 0) return 0
    return Math.round(totalMembers.value / totalGroups.value * 100) / 100
  })

  const groupsWithDrawOrder = computed(() => 
    groups.value.filter(group => group.draw_order !== null && group.draw_order !== undefined)
  )

  const groupsWithoutDrawOrder = computed(() => 
    groups.value.filter(group => group.draw_order === null || group.draw_order === undefined)
  )

  const organizationDistribution = computed(() => {
    const distribution = new Map<string, Set<string>>()
    
    groups.value.forEach(group => {
      group.organizations.forEach(org => {
        if (!distribution.has(org)) {
          distribution.set(org, new Set())
        }
        distribution.get(org)!.add(group.name)
      })
    })

    return Array.from(distribution.entries()).map(([org, groupSet]) => ({
      organization: org,
      groups: Array.from(groupSet),
      groupCount: groupSet.size
    }))
  })

  const sortedGroups = computed(() => {
    return [...groups.value].sort((a, b) => {
      // 有抽签顺序的排在前面
      if (a.draw_order !== null && b.draw_order === null) return -1
      if (a.draw_order === null && b.draw_order !== null) return 1
      
      // 都有抽签顺序，按顺序排序
      if (a.draw_order !== null && b.draw_order !== null) {
        return a.draw_order - b.draw_order
      }
      
      // 都没有抽签顺序，按名称排序
      return a.name.localeCompare(b.name)
    })
  })

  // 方法
  const fetchGroups = async () => {
    try {
      loading.value = true
      const response = await groupsApi.getList()
      groups.value = response
      appStore.updateLastUpdateTime()
    } catch (error) {
      console.error('Failed to fetch groups:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取分组列表失败',
        message: '请检查网络连接后重试'
      })
    } finally {
      loading.value = false
    }
  }

  const fetchGroupById = async (id: number) => {
    try {
      loading.value = true
      const response = await groupsApi.getById(id)
      currentGroup.value = response
      currentGroupMembers.value = response.members
      return response
    } catch (error) {
      console.error('Failed to fetch group:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取分组信息失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchGroupMembers = async (id: number) => {
    try {
      loading.value = true
      const members = await groupsApi.getMembers(id)
      currentGroupMembers.value = members
      return members
    } catch (error) {
      console.error('Failed to fetch group members:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取分组成员失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const createGroup = async (data: CreateGroupRequest) => {
    try {
      loading.value = true
      const group = await groupsApi.create(data)
      
      // 添加到列表中
      groups.value.push(group)
      
      appStore.addNotification({
        type: 'success',
        title: '创建成功',
        message: `分组 ${group.name} 创建成功`
      })
      
      return group
    } catch (error) {
      console.error('Failed to create group:', error)
      appStore.addNotification({
        type: 'error',
        title: '创建分组失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateGroup = async (id: number, data: Partial<CreateGroupRequest>) => {
    try {
      loading.value = true
      const group = await groupsApi.update(id, data)
      
      // 更新列表中的数据
      const index = groups.value.findIndex(g => g.id === id)
      if (index > -1) {
        groups.value[index] = group
      }
      
      // 更新当前分组
      if (currentGroup.value?.id === id) {
        currentGroup.value = { ...currentGroup.value, ...group }
      }
      
      appStore.addNotification({
        type: 'success',
        title: '更新成功',
        message: `分组 ${group.name} 信息已更新`
      })
      
      return group
    } catch (error) {
      console.error('Failed to update group:', error)
      appStore.addNotification({
        type: 'error',
        title: '更新分组失败',
        message: '请检查输入信息后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteGroup = async (id: number) => {
    try {
      loading.value = true
      await groupsApi.delete(id)
      
      // 从列表中移除
      const index = groups.value.findIndex(g => g.id === id)
      if (index > -1) {
        const group = groups.value[index]
        groups.value.splice(index, 1)
        
        appStore.addNotification({
          type: 'success',
          title: '删除成功',
          message: `分组 ${group.name} 已删除`
        })
      }
      
      // 清除当前分组
      if (currentGroup.value?.id === id) {
        currentGroup.value = null
        currentGroupMembers.value = []
      }
    } catch (error) {
      console.error('Failed to delete group:', error)
      appStore.addNotification({
        type: 'error',
        title: '删除分组失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const addMemberToGroup = async (groupId: number, participantId: number) => {
    try {
      loading.value = true
      await groupsApi.addMember(groupId, participantId)
      
      // 刷新分组信息
      await fetchGroups()
      if (currentGroup.value?.id === groupId) {
        await fetchGroupMembers(groupId)
      }
      
      appStore.addNotification({
        type: 'success',
        title: '添加成功',
        message: '成员已添加到分组'
      })
    } catch (error) {
      console.error('Failed to add member to group:', error)
      appStore.addNotification({
        type: 'error',
        title: '添加成员失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const removeMemberFromGroup = async (groupId: number, participantId: number) => {
    try {
      loading.value = true
      await groupsApi.removeMember(groupId, participantId)
      
      // 刷新分组信息
      await fetchGroups()
      if (currentGroup.value?.id === groupId) {
        await fetchGroupMembers(groupId)
      }
      
      appStore.addNotification({
        type: 'success',
        title: '移除成功',
        message: '成员已从分组中移除'
      })
    } catch (error) {
      console.error('Failed to remove member from group:', error)
      appStore.addNotification({
        type: 'error',
        title: '移除成员失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const assignMembersToGroup = async (groupId: number, participantIds: number[]) => {
    try {
      loading.value = true
      await groupsApi.assignMembers(groupId, participantIds)
      
      // 刷新分组信息
      await fetchGroups()
      if (currentGroup.value?.id === groupId) {
        await fetchGroupMembers(groupId)
      }
      
      appStore.addNotification({
        type: 'success',
        title: '分配成功',
        message: `已将 ${participantIds.length} 名成员分配到分组`
      })
    } catch (error) {
      console.error('Failed to assign members to group:', error)
      appStore.addNotification({
        type: 'error',
        title: '分配成员失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const autoGroupByOrganization = async (params?: {
    max_groups?: number
    min_members_per_group?: number
    max_members_per_group?: number
  }) => {
    try {
      loading.value = true
      const response = await groupsApi.autoGroupByOrganization(params)
      
      if (response.success) {
        groups.value = response.groups
        
        appStore.addNotification({
          type: 'success',
          title: '自动分组成功',
          message: response.message
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to auto group by organization:', error)
      appStore.addNotification({
        type: 'error',
        title: '自动分组失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const drawLots = async (groupIds?: number[]) => {
    try {
      loading.value = true
      const response = await groupsApi.drawLots({ group_ids: groupIds })
      
      if (response.success) {
        // 更新分组的抽签顺序
        response.results.forEach(result => {
          const group = groups.value.find(g => g.id === result.group_id)
          if (group) {
            group.draw_order = result.draw_order
          }
        })
        
        appStore.addNotification({
          type: 'success',
          title: '抽签成功',
          message: '出场顺序已确定'
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to draw lots:', error)
      appStore.addNotification({
        type: 'error',
        title: '抽签失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const setDrawOrder = async (groupId: number, order: number) => {
    try {
      loading.value = true
      await groupsApi.setDrawOrder(groupId, order)
      
      // 更新分组的抽签顺序
      const group = groups.value.find(g => g.id === groupId)
      if (group) {
        group.draw_order = order
      }
      
      appStore.addNotification({
        type: 'success',
        title: '设置成功',
        message: '出场顺序已更新'
      })
    } catch (error) {
      console.error('Failed to set draw order:', error)
      appStore.addNotification({
        type: 'error',
        title: '设置出场顺序失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchAvailableParticipants = async () => {
    try {
      loading.value = true
      const participants = await groupsApi.getAvailableParticipants()
      availableParticipants.value = participants
      return participants
    } catch (error) {
      console.error('Failed to fetch available participants:', error)
      appStore.addNotification({
        type: 'error',
        title: '获取可分组参赛者失败',
        message: '请检查网络连接后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const balanceGroups = async () => {
    try {
      loading.value = true
      const response = await groupsApi.balanceGroups()
      
      if (response.success) {
        // 刷新分组信息
        await fetchGroups()
        
        appStore.addNotification({
          type: 'success',
          title: '平衡分组成功',
          message: response.message
        })
      }
      
      return response
    } catch (error) {
      console.error('Failed to balance groups:', error)
      appStore.addNotification({
        type: 'error',
        title: '平衡分组失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const swapMembers = async (
    group1Id: number, 
    participant1Id: number, 
    group2Id: number, 
    participant2Id: number
  ) => {
    try {
      loading.value = true
      await groupsApi.swapMembers(group1Id, participant1Id, group2Id, participant2Id)
      
      // 刷新分组信息
      await fetchGroups()
      
      appStore.addNotification({
        type: 'success',
        title: '交换成功',
        message: '成员已成功交换分组'
      })
    } catch (error) {
      console.error('Failed to swap members:', error)
      appStore.addNotification({
        type: 'error',
        title: '交换成员失败',
        message: '请稍后重试'
      })
      throw error
    } finally {
      loading.value = false
    }
  }

  const clearCurrentGroup = () => {
    currentGroup.value = null
    currentGroupMembers.value = []
  }

  return {
    // 状态
    groups,
    currentGroup,
    currentGroupMembers,
    loading,
    availableParticipants,

    // 计算属性
    totalGroups,
    totalMembers,
    avgMembersPerGroup,
    groupsWithDrawOrder,
    groupsWithoutDrawOrder,
    organizationDistribution,
    sortedGroups,

    // 方法
    fetchGroups,
    fetchGroupById,
    fetchGroupMembers,
    createGroup,
    updateGroup,
    deleteGroup,
    addMemberToGroup,
    removeMemberFromGroup,
    assignMembersToGroup,
    autoGroupByOrganization,
    drawLots,
    setDrawOrder,
    fetchAvailableParticipants,
    balanceGroups,
    swapMembers,
    clearCurrentGroup
  }
})