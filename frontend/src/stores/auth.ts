import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { judgesApi } from '@/api/judges'
import type { Judge } from '@/api/types'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const currentUser = ref<Judge | null>(null)
  const token = ref<string | null>(null)
  const isLoggedIn = ref(false)
  const loginTime = ref<Date | null>(null)
  const lastActivity = ref<Date | null>(null)

  // 权限相关
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])

  // 计算属性
  const isAdmin = computed(() => 
    currentUser.value?.username === 'admin' || roles.value.includes('admin')
  )

  const isJudge = computed(() => 
    roles.value.includes('judge') || (currentUser.value && !isAdmin.value)
  )

  const userDisplayName = computed(() => 
    currentUser.value?.name || currentUser.value?.username || '未知用户'
  )

  const sessionDuration = computed(() => {
    if (!loginTime.value) return 0
    return Date.now() - loginTime.value.getTime()
  })

  // 方法
  const login = async (username: string, password: string) => {
    try {
      const response = await judgesApi.login({ username, password })
      
      if (response.success) {
        currentUser.value = response.judge
        token.value = response.token
        isLoggedIn.value = true
        loginTime.value = new Date()
        lastActivity.value = new Date()

        // 设置权限和角色
        if (username === 'admin') {
          roles.value = ['admin', 'judge']
          permissions.value = [
            'participants:read',
            'participants:write',
            'participants:delete',
            'groups:read',
            'groups:write',
            'groups:delete',
            'judges:read',
            'judges:write',
            'judges:delete',
            'scores:read',
            'scores:write',
            'scores:delete',
            'statistics:read',
            'system:manage'
          ]
        } else {
          roles.value = ['judge']
          permissions.value = [
            'participants:read',
            'scores:read',
            'scores:write',
            'statistics:read'
          ]
        }

        // 保存到localStorage
        localStorage.setItem('token', response.token)
        localStorage.setItem('currentUser', JSON.stringify(response.judge))
        localStorage.setItem('loginTime', loginTime.value.toISOString())

        return { success: true, user: response.judge }
      } else {
        throw new Error('登录失败')
      }
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await judgesApi.logout()
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // 清除状态
      currentUser.value = null
      token.value = null
      isLoggedIn.value = false
      loginTime.value = null
      lastActivity.value = null
      permissions.value = []
      roles.value = []

      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
      localStorage.removeItem('loginTime')
    }
  }

  const refreshUserInfo = async () => {
    try {
      if (!token.value) return false

      const user = await judgesApi.getCurrentJudge()
      currentUser.value = user
      lastActivity.value = new Date()

      // 更新localStorage
      localStorage.setItem('currentUser', JSON.stringify(user))
      
      return true
    } catch (error) {
      console.error('Refresh user info error:', error)
      // 如果刷新失败，可能token已过期，执行登出
      await logout()
      return false
    }
  }

  const updateLastActivity = () => {
    lastActivity.value = new Date()
  }

  const hasPermission = (permission: string): boolean => {
    return permissions.value.includes(permission) || isAdmin.value
  }

  const hasRole = (role: string): boolean => {
    return roles.value.includes(role)
  }

  const hasAnyPermission = (permissionList: string[]): boolean => {
    return permissionList.some(permission => hasPermission(permission))
  }

  const hasAllPermissions = (permissionList: string[]): boolean => {
    return permissionList.every(permission => hasPermission(permission))
  }

  // 检查会话是否有效
  const isSessionValid = (): boolean => {
    if (!isLoggedIn.value || !loginTime.value) return false
    
    // 检查会话是否超时（24小时）
    const sessionTimeout = 24 * 60 * 60 * 1000 // 24小时
    const now = Date.now()
    const sessionAge = now - loginTime.value.getTime()
    
    return sessionAge < sessionTimeout
  }

  // 初始化认证状态
  const initAuth = async () => {
    try {
      const savedToken = localStorage.getItem('token')
      const savedUser = localStorage.getItem('currentUser')
      const savedLoginTime = localStorage.getItem('loginTime')

      if (savedToken && savedUser && savedLoginTime) {
        token.value = savedToken
        currentUser.value = JSON.parse(savedUser)
        loginTime.value = new Date(savedLoginTime)
        isLoggedIn.value = true

        // 设置权限
        if (currentUser.value?.username === 'admin') {
          roles.value = ['admin', 'judge']
          permissions.value = [
            'participants:read',
            'participants:write',
            'participants:delete',
            'groups:read',
            'groups:write',
            'groups:delete',
            'judges:read',
            'judges:write',
            'judges:delete',
            'scores:read',
            'scores:write',
            'scores:delete',
            'statistics:read',
            'system:manage'
          ]
        } else {
          roles.value = ['judge']
          permissions.value = [
            'participants:read',
            'scores:read',
            'scores:write',
            'statistics:read'
          ]
        }

        // 检查会话是否有效
        if (!isSessionValid()) {
          await logout()
          return false
        }

        // 尝试刷新用户信息
        const refreshSuccess = await refreshUserInfo()
        if (!refreshSuccess) {
          return false
        }

        return true
      }
    } catch (error) {
      console.error('Init auth error:', error)
      await logout()
    }
    
    return false
  }

  // 自动登出定时器
  let autoLogoutTimer: NodeJS.Timeout | null = null

  const startAutoLogoutTimer = () => {
    if (autoLogoutTimer) {
      clearTimeout(autoLogoutTimer)
    }

    // 24小时后自动登出
    autoLogoutTimer = setTimeout(() => {
      logout()
    }, 24 * 60 * 60 * 1000)
  }

  const stopAutoLogoutTimer = () => {
    if (autoLogoutTimer) {
      clearTimeout(autoLogoutTimer)
      autoLogoutTimer = null
    }
  }

  return {
    // 状态
    currentUser,
    token,
    isLoggedIn,
    loginTime,
    lastActivity,
    permissions,
    roles,

    // 计算属性
    isAdmin,
    isJudge,
    userDisplayName,
    sessionDuration,

    // 方法
    login,
    logout,
    refreshUserInfo,
    updateLastActivity,
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAllPermissions,
    isSessionValid,
    initAuth,
    startAutoLogoutTimer,
    stopAutoLogoutTimer
  }
})