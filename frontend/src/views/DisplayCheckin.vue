<template>
  <div class="display-container">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="title-section">
        <h1 class="main-title">亚联盟杯 - 内训师大赛</h1>
        <div class="subtitle">实时签到系统</div>
      </div>
      <div class="datetime">{{ currentTime }}</div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 统计卡片区域 -->
      <div class="stats-row">
        <div class="stat-card total">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.total_participants }}</div>
            <div class="stat-label">总参赛人数</div>
          </div>
        </div>
        <div class="stat-card checked">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.checked_in }}</div>
            <div class="stat-label">已签到</div>
          </div>
        </div>
        <div class="stat-card pending">
          <div class="stat-icon">⏳</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.not_checked_in }}</div>
            <div class="stat-label">未签到</div>
          </div>
        </div>
        <div class="stat-card rate">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-number">{{ checkinStats.checkin_rate }}%</div>
            <div class="stat-label">签到率</div>
          </div>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-row">
        <!-- 左侧：各组进度 -->
        <div class="left-panel">
          <div class="panel-card">
            <div class="panel-header">
              <h3>各组签到进度</h3>
            </div>
            <div class="group-progress">
              <div 
                v-for="group in groupStats" 
                :key="group.group_name"
                class="group-item"
              >
                <div class="group-info">
                  <span class="group-name">{{ group.group_name }}</span>
                  <span class="group-ratio">{{ group.checked_in }}/{{ group.total }}</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: getProgressWidth(group) + '%' }"
                  ></div>
                </div>
                <div class="progress-percent">{{ getProgressPercent(group) }}%</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 中间：二维码 -->
        <div class="center-panel">
          <div class="qr-card">
            <div class="qr-header">
              <h3>扫码签到</h3>
            </div>
            <div class="qr-container">
              <canvas ref="qrCanvas" class="qr-code"></canvas>
            </div>
            <div class="qr-instruction">
              请使用手机扫描二维码进行签到
            </div>
          </div>
        </div>

        <!-- 右侧：最新签到 -->
        <div class="right-panel">
          <div class="panel-card">
            <div class="panel-header">
              <h3>最新签到</h3>
            </div>
            <div class="recent-list">
              <div 
                v-for="(checkin, index) in recentCheckins" 
                :key="checkin.id"
                class="recent-item"
                :class="{ 'latest': index === 0 }"
              >
                <div class="participant-avatar">
                  {{ checkin.participant_name ? checkin.participant_name.charAt(0) : '?' }}
                </div>
                <div class="participant-info">
                  <div class="participant-name">{{ checkin.participant_name || checkin.name }}</div>
                  <div class="participant-org">{{ checkin.organization }}</div>
                </div>
                <div class="checkin-time">{{ formatTime(checkin.checkin_time) }}</div>
              </div>
              <div v-if="recentCheckins.length === 0" class="no-data">
                暂无签到记录
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
import QRCode from 'qrcode'

// 响应式数据
const checkinStats = ref({
  total_participants: 0,
  checked_in: 0,
  not_checked_in: 0,
  checkin_rate: 0
})

const groupStats = ref([])
const recentCheckins = ref([])
const currentTime = ref('')

// DOM引用
const qrCanvas = ref(null)

let refreshInterval = null

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit'
  })
}

// 更新当前时间
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 计算进度宽度
const getProgressWidth = (group) => {
  if (!group.total || group.total === 0) return 0
  return Math.round((group.checked_in / group.total) * 100)
}

// 计算进度百分比
const getProgressPercent = (group) => {
  if (!group.total || group.total === 0) return 0
  return Math.round((group.checked_in / group.total) * 100)
}

// 获取签到统计
const fetchCheckinStats = async () => {
  try {
    const response = await fetch('/api/statistics/checkin')
    const data = await response.json()
    checkinStats.value = {
      total_participants: data.total_participants || 0,
      checked_in: data.checked_in || 0,
      not_checked_in: data.not_checked_in || 0,
      checkin_rate: Math.round(data.checkin_rate || 0)
    }
  } catch (error) {
    console.error('获取签到统计失败:', error)
  }
}

// 获取分组统计
const fetchGroupStats = async () => {
  try {
    const response = await fetch('/api/statistics/groups')
    const data = await response.json()
    groupStats.value = data || []
  } catch (error) {
    console.error('获取分组统计失败:', error)
  }
}

// 获取最新签到记录
const fetchRecentCheckins = async () => {
  try {
    const response = await fetch('/api/checkins/recent?limit=8')
    const data = await response.json()
    recentCheckins.value = data || []
  } catch (error) {
    console.error('获取最新签到记录失败:', error)
  }
}

// 生成二维码
const generateQRCode = async () => {
  try {
    if (qrCanvas.value) {
      const checkinUrl = `${window.location.origin}/mobile/checkin`
      
      await QRCode.toCanvas(qrCanvas.value, checkinUrl, {
        width: 280,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      })
    }
  } catch (error) {
    console.error('生成二维码失败:', error)
  }
}

// 刷新所有数据
const refreshData = async () => {
  await Promise.all([
    fetchCheckinStats(),
    fetchGroupStats(),
    fetchRecentCheckins()
  ])
}

onMounted(async () => {
  // 更新时间
  updateCurrentTime()
  setInterval(updateCurrentTime, 1000)
  
  // 生成二维码
  await generateQRCode()
  
  // 初始加载数据
  await refreshData()
  
  // 设置定时刷新
  refreshInterval = setInterval(refreshData, 3000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.display-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.title-section {
  text-align: left;
}

.main-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  background: linear-gradient(45deg, #fff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1rem;
  margin-top: 5px;
  opacity: 0.9;
  color: #e3f2fd;
}

.datetime {
  font-size: 1.3rem;
  font-weight: 500;
  color: #e3f2fd;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.main-content {
  flex: 1;
  padding: 20px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 10px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.total {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.2), rgba(103, 194, 58, 0.1));
}

.stat-card.checked {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(64, 158, 255, 0.1));
}

.stat-card.pending {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.2), rgba(245, 108, 108, 0.1));
}

.stat-card.rate {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.1));
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-number {
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 4px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
  font-weight: 500;
}

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
}

.left-panel, .center-panel, .right-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-card, .qr-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header, .qr-header {
  text-align: center;
  margin-bottom: 20px;
}

.panel-header h3, .qr-header h3 {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.group-progress {
  flex: 1;
  overflow-y: auto;
}

.group-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border-left: 4px solid #67C23A;
}

.group-info {
  min-width: 80px;
  text-align: left;
}

.group-name {
  font-weight: 600;
  font-size: 1rem;
  display: block;
}

.group-ratio {
  font-size: 0.85rem;
  opacity: 0.8;
  display: block;
  margin-top: 2px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #67C23A, #85CE61);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-percent {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  font-size: 0.9rem;
}

.qr-container {
  text-align: center;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-code {
  border-radius: 16px;
  background: white;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.qr-instruction {
  text-align: center;
  margin-top: 16px;
  font-size: 1.1rem;
  font-weight: 500;
  color: #e3f2fd;
}

.recent-list {
  flex: 1;
  overflow-y: auto;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border-left: 4px solid #409EFF;
  transition: background 0.3s ease;
}

.recent-item.latest {
  background: rgba(103, 194, 58, 0.2);
  border-left-color: #67C23A;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.participant-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.participant-info {
  flex: 1;
}

.participant-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 2px;
}

.participant-org {
  font-size: 0.85rem;
  opacity: 0.8;
}

.checkin-time {
  font-size: 0.8rem;
  opacity: 0.7;
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  opacity: 0.7;
  font-size: 1.1rem;
  color: #e3f2fd;
}

/* 滚动条样式 */
.group-progress::-webkit-scrollbar,
.recent-list::-webkit-scrollbar {
  width: 6px;
}

.group-progress::-webkit-scrollbar-track,
.recent-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.group-progress::-webkit-scrollbar-thumb,
.recent-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.group-progress::-webkit-scrollbar-thumb:hover,
.recent-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-title {
    font-size: 1.8rem;
  }
  
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
}
</style>