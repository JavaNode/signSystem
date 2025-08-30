import api from './index'

export const statisticsApi = {
  // 获取总览统计
  getOverview: () => api.get('/api/statistics/overview'),
  
  // 获取签到统计
  getCheckinStats: () => api.get('/api/statistics/checkin'),
  
  // 获取评分统计
  getScoreStats: () => api.get('/api/statistics/scores'),
  
  // 获取分组统计
  getGroupStats: () => api.get('/api/statistics/groups'),
  
  // 导出数据
  exportData: (type: string) => api.get(`/api/statistics/export/${type}`, {
    responseType: 'blob'
  })
}