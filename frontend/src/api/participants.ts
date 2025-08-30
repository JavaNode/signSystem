import api from './index'

export const participantsApi = {
  // 获取参赛者列表
  getList: () => api.get('/api/participants'),
  
  // 根据ID获取参赛者
  getById: (id: number) => api.get(`/api/participants/${id}`),
  
  // 根据二维码获取参赛者
  getByQR: (qrId: string) => api.get(`/api/participants/qr/${qrId}`),
  
  // 获取参赛者二维码
  getQRCode: (id: number) => api.get(`/api/participants/${id}/qrcode`),
  
  // 创建参赛者
  create: (data: any) => api.post('/api/participants', data),
  
  // 更新参赛者
  update: (id: number, data: any) => api.put(`/api/participants/${id}`, data),
  
  // 删除参赛者
  delete: (id: number) => api.delete(`/api/participants/${id}`)
}