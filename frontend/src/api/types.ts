// API响应基础类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 参赛者类型
export interface Participant {
  id: number
  name: string
  organization: string
  phone: string
  phone_last4: string
  photo_path?: string
  group_id?: number
  group_name?: string
  qr_code_id: string
  is_checked_in: boolean
  checkin_time?: string
  created_at: string
  updated_at: string
}

// 分组类型
export interface Group {
  id: number
  name: string
  description?: string
  draw_order?: number
  member_count: number
  organizations: string[]
  created_at: string
  updated_at: string
}

// 评委类型
export interface Judge {
  id: number
  name: string
  username: string
  organization: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// 评分类型
export interface Score {
  id: number
  participant_id: number
  participant_name: string
  judge_id: number
  judge_name: string
  score: number
  created_at: string
}

// 签到日志类型
export interface CheckinLog {
  id: number
  participant_id: number
  participant_name: string
  organization: string
  checkin_time: string
  ip_address?: string
  user_agent?: string
}

// 统计数据类型
export interface Statistics {
  total_participants: number
  checked_in_count: number
  checkin_rate: number
  total_groups: number
  total_judges: number
  total_scores: number
  avg_score: number
  checkin_by_organization: Array<{
    organization: string
    total: number
    checked_in: number
    rate: number
  }>
  checkin_timeline: Array<{
    time: string
    count: number
  }>
  score_distribution: Array<{
    range: string
    count: number
  }>
}

// 签到验证请求
export interface CheckinVerifyRequest {
  qr_code_id: string
  phone_last4: string
  name: string
}

// 评委登录请求
export interface JudgeLoginRequest {
  username: string
  password: string
}

// 评分提交请求
export interface ScoreSubmitRequest {
  participant_id: number
  score: number
}

// 创建参赛者请求
export interface CreateParticipantRequest {
  name: string
  organization: string
  phone: string
  group_id?: number
}

// 创建分组请求
export interface CreateGroupRequest {
  name: string
  description?: string
}

// 创建评委请求
export interface CreateJudgeRequest {
  name: string
  username: string
  password: string
  organization: string
}

// 批量导入参赛者请求
export interface ImportParticipantsRequest {
  participants: Array<{
    name: string
    organization: string
    phone: string
  }>
}

// 抽签请求
export interface DrawLotsRequest {
  group_ids?: number[]
}

// 文件上传响应
export interface FileUploadResponse {
  filename: string
  path: string
  size: number
  url: string
}