<template>
  <div class="dashboard">
    <div class="header">
      <h1>🏆 联盟杯内训师大赛管理系统</h1>
      <p class="subtitle">比赛管理控制台</p>
    </div>

    <div class="main-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.total_participants || 0 }}</div>
            <div class="stat-label">总参赛者</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.checked_in || 0 }}</div>
            <div class="stat-label">已签到</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-number">{{ scoreStats.total_scores || 0 }}</div>
            <div class="stat-label">评分数量</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.checkin_rate || 0 }}%</div>
            <div class="stat-label">签到率</div>
          </div>
        </div>
      </div>

      <!-- 公共二维码区域 -->
      <div class="qr-section">
        <h3>📱 签到二维码</h3>
        
        <div class="public-qr">
          <h4>🔗 公共签到二维码</h4>
          <p class="qr-description">参赛者扫描此二维码进行签到</p>
          <div class="qr-display" v-if="publicQRCode">
            <img :src="publicQRCode" alt="公共签到二维码" class="qr-image" />
            <div class="qr-links">
              <a href="/mobile/checkin" target="_blank" class="qr-link">
                📱 移动端签到页面
              </a>
              <a href="/judge/score" target="_blank" class="qr-link">
                👨‍⚖️ 评委打分页面
              </a>
            </div>
          </div>
          <button @click="loadPublicQRCode" class="generate-btn">
            {{ publicQRCode ? '刷新二维码' : '生成二维码' }}
          </button>
        </div>
      </div>

      <!-- 参赛者列表 -->
      <div class="participants-section">
        <h3>👥 参赛者列表</h3>
        <div class="participants-grid">
          <div 
            v-for="participant in participants" 
            :key="participant.id"
            class="participant-card"
            :class="{ 'checked-in': participant.is_checked_in }"
          >
            <div class="participant-info">
              <div class="name">{{ participant.name }}</div>
              <div class="org">{{ participant.organization }}</div>
              <div class="group">{{ participant.group_name }}</div>
              <div class="status">
                {{ participant.is_checked_in ? '✅ 已签到' : '⏳ 未签到' }}
              </div>
              <div v-if="participant.checkin_time" class="checkin-time">
                {{ formatTime(participant.checkin_time) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const participants = ref([])
const checkinStats = ref({})
const scoreStats = ref({})
const publicQRCode = ref('')

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

const loadData = async () => {
  try {
    // 加载参赛者数据
    const participantsRes = await api.get('/participants')
    participants.value = participantsRes.data

    // 加载签到统计
    const checkinRes = await api.get('/statistics/checkin')
    checkinStats.value = checkinRes.data

    // 加载评分统计
    const scoresRes = await api.get('/statistics/scores')
    scoreStats.value = scoresRes.data

    // 加载公共二维码
    await loadPublicQRCode()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const loadPublicQRCode = async () => {
  try {
    const response = await api.get('/qrcode/public')
    publicQRCode.value = response.data.qr_code_data
  } catch (error) {
    console.error('加载公共二维码失败:', error)
  }
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
  // 每30秒刷新一次数据
  setInterval(loadData, 30000)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 32px;
  color: #2d3748;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.subtitle {
  font-size: 18px;
  color: #718096;
  margin: 0;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 40px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #718096;
}

.qr-section, .participants-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.qr-section h3, .participants-section h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 20px;
}

.public-qr {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  text-align: center;
}

.public-qr h4 {
  margin: 0 0 10px 0;
  font-size: 20px;
}

.qr-description {
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.qr-display {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  display: inline-block;
}

.qr-image {
  width: 200px;
  height: 200px;
  border-radius: 8px;
}

.qr-links {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.qr-link {
  display: inline-block;
  padding: 8px 16px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: background 0.2s;
}

.qr-link:hover {
  background: #5a67d8;
}

.generate-btn {
  padding: 12px 24px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.generate-btn:hover {
  background: rgba(255,255,255,0.3);
}

.participants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.participant-card {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}

.participant-card.checked-in {
  border-color: #48bb78;
  background: #f0fff4;
}

.participant-card .name {
  font-weight: 600;
  font-size: 16px;
  color: #2d3748;
  margin-bottom: 4px;
}

.participant-card .org {
  font-size: 14px;
  color: #718096;
  margin-bottom: 4px;
}

.participant-card .group {
  font-size: 14px;
  color: #667eea;
  margin-bottom: 8px;
}

.participant-card .status {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.participant-card .checkin-time {
  font-size: 12px;
  color: #718096;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .participants-grid {
    grid-template-columns: 1fr;
  }
}
</style>