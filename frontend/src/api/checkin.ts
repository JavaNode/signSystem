import api from './index'

export const checkinApi = {
  // 验证签到信息
  verify: (data: { qr_code_id: string; phone_last4: string; name: string }) => 
    api.post('/api/checkin/verify', data),
  
  // 获取签到统计
  getStats: () => api.get('/api/checkin/stats'),
  
  // 获取签到日志
  getLogs: () => api.get('/api/checkin/logs')
}