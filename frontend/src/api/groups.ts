import api from './index'

export const groupsApi = {
  // 获取分组列表
  getList: () => api.get('/api/groups'),
  
  // 根据ID获取分组详情
  getById: (id: number) => api.get(`/api/groups/${id}`),
  
  // 创建分组
  create: (data: any) => api.post('/api/groups', data),
  
  // 更新分组
  update: (id: number, data: any) => api.put(`/api/groups/${id}`, data),
  
  // 删除分组
  delete: (id: number) => api.delete(`/api/groups/${id}`),
  
  // 抽签
  drawLots: () => api.post('/api/groups/draw')
}