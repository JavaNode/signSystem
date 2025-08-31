<template>
  <div class="dashboard">
    <!-- 移动端实时时间显示 -->
    <div class="mobile-time" v-if="isMobile">
      {{ currentTime }}
    </div>
    
    <div class="header">
      <h1>🏆 {{ isMobile ? '亚联盟杯 - 内训师大赛' : '联盟杯内训师大赛管理系统' }}</h1>
      <p class="subtitle">{{ isMobile ? '实时签到系统' : '比赛管理控制台' }}</p>
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
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

import { getApiBaseUrl } from '../config'

const participants = ref([])
const checkinStats = ref({})
const scoreStats = ref({})
const publicQRCode = ref('')

// 移动端检测和时间显示
const isMobile = ref(false)
const currentTime = ref('')
let timeInterval = null

// 检测是否为移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  currentTime.value = `${year}/${month}/${day}
${hours}:${minutes}:${seconds}`
}

const api = axios.create({
  baseURL: getApiBaseUrl()
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
  checkMobile()
  updateTime()
  
  // 每30秒刷新一次数据
  setInterval(loadData, 30000)
  
  // 每秒更新时间
  timeInterval = setInterval(updateTime, 1000)
  
  // 监听窗口大小变化
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  window.removeEventListener('resize', checkMobile)
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

/* 移动端时间显示 */
.mobile-time {
  position: fixed;
  top: 15px;
  right: 15px;
  color: white;
  font-size: 12px;
  text-align: right;
  line-height: 1.2;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.2);
  padding: 8px 12px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  white-space: pre-line;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .dashboard {
    padding: 8px;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .header {
    text-align: center;
    margin-bottom: 20px;
    padding: 15px 10px;
  }
  
  .header h1 {
    font-size: 18px;
    margin-bottom: 5px;
    color: white;
    font-weight: 600;
  }
  
  .header .subtitle {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    margin: 0;
  }
  
  /* 统计卡片移动端优化 */
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .stat-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 20px 15px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  
  .stat-card .stat-icon {
    font-size: 24px;
    margin-bottom: 8px;
    display: block;
  }
  
  .stat-card .stat-number {
    font-size: 32px;
    font-weight: 700;
    color: white;
    margin-bottom: 4px;
    line-height: 1;
  }
  
  .stat-card .stat-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
    white-space: nowrap;
  }
  
  /* 隐藏移动端不需要的内容 */
  .qr-section,
  .participants-section {
    display: none;
  }
  
  /* 添加实时时间显示 */
  .dashboard::before {
    content: '';
    position: fixed;
    top: 10px;
    right: 15px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 12px;
    z-index: 1000;
  }
  
  /* 添加移动端专用的底部导航提示 */
  .dashboard::after {
    content: '← 滑动查看更多 →';
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255, 255, 255, 0.6);
    font-size: 12px;
    text-align: center;
  }
}

/* 超小屏幕适配 (iPhone SE等) */
@media (max-width: 375px) {
  .stats-grid {
    gap: 8px;
  }
  
  .stat-card {
    padding: 15px 10px;
    min-height: 100px;
  }
  
  .stat-card .stat-number {
    font-size: 28px;
  }
  
  .stat-card .stat-label {
    font-size: 11px;
  }
  
  .header h1 {
    font-size: 16px;
  }
}

/* 横屏模式适配 */
@media (max-width: 768px) and (orientation: landscape) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  
  .stat-card {
    min-height: 80px;
    padding: 10px;
  }
  
  .stat-card .stat-number {
    font-size: 24px;
  }
  
  .header {
    padding: 10px;
    margin-bottom: 15px;
  }
  
  .header h1 {
    font-size: 16px;
  }
}
</style>