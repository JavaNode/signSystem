<template>
  <div class="mobile-checkin">
    <!-- 头部区域 -->
    <div class="header">
      <div class="header-bg"></div>
      <div class="header-content">
        <div class="logo">
          <el-icon class="logo-icon"><Trophy /></el-icon>
        </div>
        <h1 class="title">联盟杯内训师大赛</h1>
        <p class="subtitle">参赛者签到系统</p>
      </div>
    </div>

    <!-- 签到表单 -->
    <div class="checkin-container" v-if="!isCheckedIn">
      <div class="form-card">
        <div class="form-header">
          <el-icon class="form-icon"><UserFilled /></el-icon>
          <h2>请验证身份信息</h2>
          <p>输入您的手机号后四位和真实姓名完成签到</p>
        </div>

        <el-form 
          :model="form" 
          :rules="rules" 
          ref="formRef"
          label-position="top"
          size="large"
        >
          <el-form-item label="手机号后四位" prop="phone_last4">
            <el-input
              v-model="form.phone_last4"
              placeholder="请输入手机号后四位"
              maxlength="4"
              clearable
            >
              <template #prefix>
                <el-icon><Cellphone /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="真实姓名" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入真实姓名"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large"
              :loading="loading"
              @click="submitCheckin"
              class="checkin-btn"
            >
              <el-icon v-if="!loading"><CircleCheck /></el-icon>
              {{ loading ? '验证中...' : '确认签到' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 签到成功页面 -->
    <div class="success-container" v-if="isCheckedIn">
      <div class="success-card">
        <div class="success-animation">
          <el-icon class="success-icon"><CircleCheckFilled /></el-icon>
          <div class="success-ripple"></div>
        </div>
        
        <h2 class="success-title">签到成功！</h2>
        <p class="success-subtitle">欢迎参加联盟杯内训师大赛</p>

        <!-- 参赛者信息 -->
        <div class="participant-info">
          <div class="info-item">
            <span class="info-label">姓名</span>
            <span class="info-value">{{ participantInfo.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">单位</span>
            <span class="info-value">{{ participantInfo.organization }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">分组</span>
            <span class="info-value">{{ participantInfo.group_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">签到时间</span>
            <span class="info-value">{{ formatTime(participantInfo.checkin_time) }}</span>
          </div>
        </div>

        <!-- 比赛信息 -->
        <div class="competition-info">
          <h3>
            <el-icon><InfoFilled /></el-icon>
            比赛信息
          </h3>
          <div class="competition-details">
            <p><strong>比赛名称：</strong>{{ competitionInfo.name || '联盟杯内训师大赛' }}</p>
            <p><strong>比赛日期：</strong>{{ competitionInfo.date || '2024年9月24日' }}</p>
            <p><strong>比赛地点：</strong>{{ competitionInfo.location || '待通知' }}</p>
          </div>
        </div>

        <!-- 温馨提示 -->
        <div class="tips">
          <h4>
            <el-icon><BellFilled /></el-icon>
            温馨提示
          </h4>
          <ul>
            <li>请按时参加比赛，提前15分钟到场</li>
            <li>比赛期间请保持手机静音</li>
            <li>如有疑问请联系现场工作人员</li>
            <li>祝您比赛顺利，取得好成绩！</li>
          </ul>
        </div>

        <el-button 
          type="primary" 
          size="large"
          @click="resetForm"
          class="reset-btn"
        >
          <el-icon><RefreshLeft /></el-icon>
          重新签到
        </el-button>
      </div>
    </div>

    <!-- 错误提示 -->
    <el-dialog
      v-model="showError"
      title="签到失败"
      width="90%"
      :show-close="false"
    >
      <div class="error-content">
        <el-icon class="error-icon"><CircleCloseFilled /></el-icon>
        <p>{{ errorMessage }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showError = false">
          我知道了
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const isCheckedIn = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const formRef = ref<FormInstance>()

const form = reactive({
  phone_last4: '',
  name: ''
})

const participantInfo = ref({})
const competitionInfo = ref({})

// 表单验证规则
const rules: FormRules = {
  phone_last4: [
    { required: true, message: '请输入手机号后四位', trigger: 'blur' },
    { len: 4, message: '请输入4位数字', trigger: 'blur' },
    { pattern: /^\d{4}$/, message: '请输入正确的数字', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在2到10个字符', trigger: 'blur' }
  ]
}

// API配置
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 方法
const submitCheckin = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    const response = await api.post('/mobile/checkin', {
      qr_code_id: '',
      phone_last4: form.phone_last4,
      name: form.name
    })

    if (response.data.success) {
      isCheckedIn.value = true
      participantInfo.value = response.data.participant
      competitionInfo.value = response.data.competition_info || {}
      ElMessage.success('签到成功！')
    } else {
      showErrorDialog(response.data.message)
    }
  } catch (error: any) {
    console.error('签到失败:', error)
    showErrorDialog(error.response?.data?.detail || '签到失败，请重试')
  } finally {
    loading.value = false
  }
}

const showErrorDialog = (message: string) => {
  errorMessage.value = message
  showError.value = true
}

const resetForm = () => {
  isCheckedIn.value = false
  form.phone_last4 = ''
  form.name = ''
  participantInfo.value = {}
  competitionInfo.value = {}
  formRef.value?.resetFields()
}

const formatTime = (timeString: string) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.mobile-checkin {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
}

.header {
  position: relative;
  padding: 60px 20px 40px;
  text-align: center;
  color: white;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="white" opacity="0.1"><polygon points="0,0 1000,0 1000,60 0,100"/></svg>') no-repeat center bottom;
  background-size: cover;
}

.header-content {
  position: relative;
  z-index: 1;
}

.logo {
  margin-bottom: 20px;
}

.logo-icon {
  font-size: 48px;
  color: #FFD700;
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

.checkin-container {
  padding: 0 20px 40px;
}

.form-card {
  background: white;
  border-radius: 24px;
  padding: 32px 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-icon {
  font-size: 40px;
  color: #667eea;
  margin-bottom: 16px;
}

.form-header h2 {
  font-size: 24px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.form-header p {
  color: #7f8c8d;
  margin: 0;
  font-size: 14px;
}

.checkin-btn {
  width: 100%;
  height: 56px;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.checkin-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
}

.success-container {
  padding: 0 20px 40px;
}

.success-card {
  background: white;
  border-radius: 24px;
  padding: 40px 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  text-align: center;
}

.success-animation {
  position: relative;
  margin-bottom: 32px;
}

.success-icon {
  font-size: 80px;
  color: #67C23A;
  position: relative;
  z-index: 2;
}

.success-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 3px solid #67C23A;
  border-radius: 50%;
  opacity: 0.3;
  animation: ripple 2s infinite;
}

@keyframes ripple {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0.6;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0;
  }
}

.success-title {
  font-size: 28px;
  color: #2c3e50;
  margin: 0 0 8px 0;
  font-weight: bold;
}

.success-subtitle {
  color: #7f8c8d;
  margin: 0 0 32px 0;
  font-size: 16px;
}

.participant-info {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  text-align: left;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e9ecef;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #495057;
}

.info-value {
  color: #2c3e50;
  font-weight: 500;
}

.competition-info, .tips {
  background: #e3f2fd;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  text-align: left;
}

.competition-info h3, .tips h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  color: #1976d2;
  font-size: 18px;
}

.competition-details p {
  margin: 8px 0;
  color: #2c3e50;
}

.tips {
  background: #fff3cd;
}

.tips h4 {
  color: #856404;
}

.tips ul {
  margin: 0;
  padding-left: 20px;
}

.tips li {
  margin-bottom: 8px;
  color: #856404;
  line-height: 1.5;
}

.reset-btn {
  width: 100%;
  height: 48px;
  border-radius: 16px;
  font-size: 16px;
  background: #6c757d;
  border: none;
}

.error-content {
  text-align: center;
  padding: 20px;
}

.error-icon {
  font-size: 48px;
  color: #F56C6C;
  margin-bottom: 16px;
}

.error-content p {
  font-size: 16px;
  color: #2c3e50;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .header {
    padding: 40px 15px 30px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .form-card, .success-card {
    padding: 24px 20px;
    border-radius: 20px;
  }
  
  .checkin-container, .success-container {
    padding: 0 15px 30px;
  }
}
</style>