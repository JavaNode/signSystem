import api from './index'

export const judgesApi = {
  // 评委登录
  login: (data: { username: string; password: string }) => 
    api.post('/api/judges/login', data),
  
  // 获取评委列表
  getList: () => api.get('/api/judges'),
  
  // 创建评委
  create: (data: any) => api.post('/api/judges', data),
  
  // 更新评委
  update: (id: number, data: any) => api.put(`/api/judges/${id}`, data),
  
  // 删除评委
  delete: (id: number) => api.delete(`/api/judges/${id}`)
}