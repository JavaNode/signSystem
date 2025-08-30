import api from './index'

export const scoresApi = {
  // 提交评分
  submit: (data: { participant_id: number; score: number }) => 
    api.post('/api/scores', data),
  
  // 获取评分列表
  getList: () => api.get('/api/scores'),
  
  // 获取参赛者评分
  getByParticipant: (participantId: number) => 
    api.get(`/api/scores/participant/${participantId}`),
  
  // 获取评委评分
  getByJudge: (judgeId: number) => 
    api.get(`/api/scores/judge/${judgeId}`),
  
  // 获取排行榜
  getRanking: () => api.get('/api/scores/ranking')
}