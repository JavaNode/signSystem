<template>
  <div class="judge-score">
    <!-- 登录页面 -->
    <div class="login-page" v-if="!isLoggedIn">
      <div class="header">
        <div class="logo">
          <el-icon class="logo-icon"><Medal /></el-icon>
        </div>
        <h1 class="title">评委打分系统</h1>
        <p class="subtitle">联盟杯内训师大赛</p>
      </div>

      <div class="login-container">
        <div class="login-card">
          <div class="login-header">
            <el-icon class="login-icon"><UserFilled /></el-icon>
            <h2>评委登录</h2>
            <p>请输入您的评委账号信息</p>
          </div>

          <el-form 
            :model="loginForm" 
            :rules="loginRules" 
            ref="loginFormRef"
            label-position="top"
            size="large"
          >
            <el-form-item label="评委编号" prop="judge_code">
              <el-input
                v-model="loginForm.judge_code"
                placeholder="请输入评委编号"
                clearable
              >
                <template #prefix>
                  <el-icon><Postcard /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="登录密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入登录密码"
                show-password
                clearable
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                size="large"
                :loading="loginLoading"
                @click="handleLogin"
                class="login-btn"
              >
                <el-icon v-if="!loginLoading"><Right /></el-icon>
                {{ loginLoading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 测试账号提示 -->
          <div class="demo-accounts">
            <el-alert
              title="测试账号"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>评委编号: judge01 | 密码: 123456</p>
                <p>评委编号: judge02 | 密码: 123456</p>
              </template>
            </el-alert>
          </div>
        </div>
      </div>
    </div>

    <!-- 打分页面 -->
    <div class="score-page" v-if="isLoggedIn">
      <!-- 顶部信息栏 -->
      <div class="score-header">
        <div class="judge-info">
          <el-avatar :size="40" class="judge-avatar">
            <el-icon><UserFilled /></el-icon>
          </el-avatar>
          <div class="judge-details">
            <div class="judge-name">{{ judgeInfo.name }}</div>
            <div class="judge-code">{{ judgeInfo.judge_code }}</div>
          </div>
        </div>
        <el-button @click="handleLogout" type="danger" plain>
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-container">
        <el-row :gutter="12">
          <el-col :span="8">
            <div class="stat-card total">
              <div class="stat-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.total_participants }}</div>
                <div class="stat-label">总参赛者</div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-card scored">
              <div class="stat-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.scored_count }}</div>
                <div class="stat-label">已打分</div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-card pending">
              <div class="stat-icon">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ statistics.pending_count }}</div>
                <div class="stat-label">待打分</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 参赛者列表 -->
      <div class="participants-container">
        <div class="container-header">
          <h3>
            <el-icon><List /></el-icon>
            参赛者评分
          </h3>
          <el-button @click="loadParticipants" :loading="loading" size="small">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div class="participants-list" v-loading="loading">
          <div 
            v-for="participant in participants" 
            :key="participant.id"
            class="participant-card"
            :class="{ 'scored': participant.scored }"
          >
            <div class="participant-info">
              <div class="participant-avatar">
                <el-avatar :size="50">
                  {{ participant.name.charAt(0) }}
                </el-avatar>
              </div>
              <div class="participant-details">
                <div class="participant-name">{{ participant.name }}</div>
                <div class="participant-org">{{ participant.organization }}</div>
                <div class="participant-group">
                  <el-tag size="small" type="info">{{ participant.group_name }}</el-tag>
                </div>
              </div>
            </div>

            <div class="score-section">
              <!-- 当前分数显示 -->
              <div v-if="participant.scored" class="current-score">
                <div class="score-display">
                  <span class="score-number">{{ participant.score }}</span>
                  <span class="score-unit">分</span>
                </div>
                <div class="score-status">已评分</div>
              </div>

              <!-- 评分输入 -->
              <div class="score-input">
                <div class="score-slider-container">
                  <el-slider
                    v-model="participant.newScore"
                    :min="0"
                    :max="10"
                    :step="0.1"
                    :format-tooltip="formatTooltip"
                    show-input
                    :show-input-controls="true"
                    class="score-slider"
                  />
                  <div class="score-display-large">
                    {{ participant.newScore || 0 }} 分
                  </div>
                </div>
                <el-button 
                  type="primary"
                  size="large"
                  @click="submitScore(participant)"
                  :disabled="!isValidScore(participant.newScore)"
                  :loading="participant.submitting"
                  class="submit-score-btn"
                >
                  <el-icon><Check /></el-icon>
                  {{ participant.scored ? '更新' : '提交' }}
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && participants.length === 0"
          description="暂无已签到的参赛者"
          :image-size="120"
        />
      </div>
    </div>

    <!-- 成功提示 -->
    <el-notification
      v-if="showSuccess"
      title="评分成功"
      :message="successMessage"
      type="success"
      :duration="3000"
      @close="showSuccess = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'

// 响应式数据
const isLoggedIn = ref(false)
const loginLoading = ref(false)
const loading = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

const loginFormRef = ref<FormInstance>()
const judgeInfo = ref({})
const participants = ref([])
const statistics = ref({
  total_participants: 0,
  scored_count: 0,
  pending_count: 0
})

const loginForm = reactive({
  judge_code: '',
  password: ''
})

// 表单验证规则
const loginRules: FormRules = {
  judge_code: [
    { required: true, message: '请输入评委编号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' }
  ]
}

// API配置
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 方法
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    loginLoading.value = true

    const response = await api.post('/mobile/judge/login', loginForm)
    
    if (response.data.success) {
      isLoggedIn.value = true
      judgeInfo.value = response.data.judge
      ElMessage.success('登录成功')
      await loadParticipants()
    }
  } catch (error: any) {
    console.error('登录失败:', error)
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loginLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    isLoggedIn.value = false
    judgeInfo.value = {}
    participants.value = []
    loginForm.judge_code = ''
    loginForm.password = ''
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}

const loadParticipants = async () => {
  if (!judgeInfo.value.id) return
  
  try {
    loading.value = true
    const response = await api.get(`/mobile/judge/${judgeInfo.value.id}/participants`)
    
    participants.value = response.data.participants.map(p => ({
      ...p,
      newScore: p.score || null,
      submitting: false
    }))
    
    statistics.value = {
      total_participants: response.data.total_participants || 0,
      scored_count: response.data.scored_count || 0,
      pending_count: response.data.pending_count || 0
    }
  } catch (error) {
    console.error('加载参赛者失败:', error)
    ElMessage.error('加载参赛者失败')
  } finally {
    loading.value = false
  }
}

const isValidScore = (score: number | null) => {
  return score !== null && score >= 0 && score <= 10
}

const formatTooltip = (value: number) => {
  return `${value} 分`
}

const submitScore = async (participant: any) => {
  if (!isValidScore(participant.newScore)) {
    ElMessage.warning('请输入0-10之间的分数')
    return
  }

  try {
    participant.submitting = true

    const response = await api.post('/mobile/scores/submit', {
      participant_id: participant.id,
      judge_id: judgeInfo.value.id,
      score: participant.newScore
    })

    if (response.data.success) {
      participant.scored = true
      participant.score = participant.newScore
      
      // 显示成功通知
      ElNotification({
        title: '评分成功',
        message: `已为 ${participant.name} 评分：${participant.newScore} 分`,
        type: 'success',
        duration: 3000
      })
      
      // 重新加载统计数据
      await loadParticipants()
    }
  } catch (error: any) {
    console.error('提交评分失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    participant.submitting = false
  }
}

// 生命周期
onMounted(() => {
  // 可以在这里检查是否有保存的登录状态
})
</script>

<style scoped>
.judge-score {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 登录页面样式 */
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  color: white;
  padding: 60px 20px 40px;
}

.logo-icon {
  font-size: 48px;
  color: #FFD700;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

.title {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 10px 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.login-container {
  flex: 1;
  padding: 0 20px 40px;
}

.login-card {
  background: white;
  border-radius: 24px;
  padding: 32px 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  max-width: 400px;
  margin: 0 auto;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  font-size: 40px;
  color: #667eea;
  margin-bottom: 16px;
}

.login-header h2 {
  font-size: 24px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.login-header p {
  color: #7f8c8d;
  margin: 0;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 56px;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
}

.demo-accounts {
  margin-top: 24px;
}

.demo-accounts :deep(.el-alert__content) {
  font-size: 13px;
}

.demo-accounts p {
  margin: 4px 0;
}

/* 打分页面样式 */
.score-page {
  min-height: 100vh;
  padding: 20px;
}

.score-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.judge-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.judge-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.judge-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.judge-code {
  font-size: 14px;
  color: #7f8c8d;
}

.stats-container {
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-card.scored .stat-icon {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #E6A23C, #f0a020);
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 12px;
  color: #7f8c8d;
}

.participants-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
}

.container-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.container-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.participants-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.participant-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.participant-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.participant-card.scored {
  border-left: 4px solid #67C23A;
}

.participant-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.participant-avatar {
  flex-shrink: 0;
}

.participant-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.participant-org {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.score-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  min-width: 200px;
}

.current-score {
  text-align: center;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
  justify-content: center;
}

.score-number {
  font-size: 24px;
  font-weight: bold;
  color: #67C23A;
}

.score-unit {
  font-size: 14px;
  color: #7f8c8d;
}

.score-status {
  font-size: 12px;
  color: #67C23A;
}

.score-input {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: stretch;
}

.score-slider-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.score-slider {
  width: 100%;
}

.score-display-large {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
  padding: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
}

.submit-score-btn {
  border-radius: 8px;
  height: 48px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .score-page {
    padding: 15px;
  }
  
  .score-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .participant-card {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .participant-info {
    justify-content: flex-start;
  }
  
  .score-section {
    align-items: stretch;
  }
  
  .score-input {
    justify-content: space-between;
  }
}
</style>