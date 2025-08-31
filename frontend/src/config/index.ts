/**
 * 前端配置管理
 */

interface AppConfig {
  // API配置
  apiBaseUrl: string
  apiTimeout: number
  
  // 应用配置
  appTitle: string
  appVersion: string
  
  // 环境配置
  isDevelopment: boolean
  isProduction: boolean
  
  // 功能配置
  enableDebug: boolean
  enableMock: boolean
}

// 从环境变量获取配置
const getEnvConfig = (): Partial<AppConfig> => {
  return {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
    appTitle: import.meta.env.VITE_APP_TITLE || '联盟杯内训师大赛管理系统',
    appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
    enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
    enableMock: import.meta.env.VITE_ENABLE_MOCK === 'true'
  }
}

// 默认配置
const defaultConfig: AppConfig = {
  apiBaseUrl: 'http://localhost:8000',
  apiTimeout: 10000,
  appTitle: '联盟杯内训师大赛管理系统',
  appVersion: '1.0.0',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  enableDebug: import.meta.env.DEV,
  enableMock: false
}

// 合并配置
const config: AppConfig = {
  ...defaultConfig,
  ...getEnvConfig()
}

// 导出配置
export default config

// 导出常用配置
export const {
  apiBaseUrl,
  apiTimeout,
  appTitle,
  appVersion,
  isDevelopment,
  isProduction,
  enableDebug,
  enableMock
} = config

// 获取完整的API地址
export const getApiUrl = (path: string = ''): string => {
  const baseUrl = apiBaseUrl.endsWith('/') ? apiBaseUrl.slice(0, -1) : apiBaseUrl
  const apiPath = path.startsWith('/') ? path : `/${path}`
  return `${baseUrl}${apiPath}`
}

// 获取API基础地址（带/api路径）
export const getApiBaseUrl = (): string => {
  return getApiUrl('/api')
}

// 调试日志
if (enableDebug) {
  console.log('🔧 前端配置:', config)
}