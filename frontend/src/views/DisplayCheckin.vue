<template>
  <div class="display-checkin">
    <!-- 顶部标题栏 -->
    <div class="display-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon class="logo-icon"><Trophy /></el-icon>
          <div class="title-section">
            <h1 class="main-title">联盟杯内训师大赛</h1>
            <p class="sub-title">实时签到展示大屏</p>
          </div>
        </div>
        <div class="time-section">
          <div class="current-time">{{ currentTime }}</div>
          <div class="current-date">{{ currentDate }}</div>
        </div>
      </div>
    </div>

    <!-- 统计数据区域 -->
    <div class="stats-section">
      <div class="stats-container">
        <div class="stat-card total-card">
          <div class="stat-icon">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalParticipants }}</div>
            <div class="stat-label">总参赛者</div>
          </div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div class="progress-fill total-fill" :style="{ width: '100%' }"></div>
            </div>
          </div>
        </div>

        <div class="stat-card checkin-card">
          <div class="stat-icon">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.checkedIn }}</div>
            <div class="stat-label">已签到</div>
          </div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill checkin-fill" 
                :style="{ width: checkinProgress + '%' }"
              ></div>
            </div>
            <div class="progress-text">{{ checkinProgress }}%</div>
          </div>
        </div>

        <div class="stat-card pending-card">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalParticipants - stats.checkedIn }}</div>
            <div class="stat-label">未签到</div>
          </div>
          <div class="stat-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill pending-fill" 
                :style="{ width: (100 - checkinProgress) + '%' }"
              ></div>
            </div>
            <div class="progress-text">{{ 100 - checkinProgress }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：最新签到动态 -->
      <div class="left-panel">
        <div class="panel-header">
          <el-icon><Notification /></el-icon>
          <h3>最新签到动态</h3>
          <div class="refresh-indicator" :class="{ 'active': isRefreshing }">
            <el-icon><Refresh /></el-icon>
          </div>
        </div>
        
        <div class="recent-checkins">
          <transition-group name="checkin-item" tag="div">
            <div 
              v-for="checkin in recentCheckins" 
              :key="checkin.id"
              class="checkin-item"
            >
              <div class="checkin-avatar">
                <el-avatar :size="50">
                  {{ checkin.name.charAt(0) }}
                </el-avatar>
                <div class="checkin-status">
                  <el-icon><CircleCheckFilled /></el-icon>
                </div>
              </div>
              <div class="checkin-info">
                <div class="checkin-name">{{ checkin.name }}</div>
                <div class="checkin-org">{{ checkin.organization }}</div>
                <div class="checkin-time">{{ formatTime(checkin.checkin_time) }}</div>
              </div>
              <div class="checkin-animation">
                <div class="success-ripple"></div>
              </div>
            </div>
          </transition-group>
        </div>

        <!-- 空状态 -->
        <div v-if="recentCheckins.length === 0" class="empty-checkins">
          <el-icon class="empty-icon"><DocumentRemove /></el-icon>
          <p>暂无签到记录</p>
        </div>
      </div>

      <!-- 右侧：签到统计图表 -->
      <div class="right-panel">
        <div class="panel-header">
          <el-icon><DataAnalysis /></el-icon>
          <h3>签到统计图表</h3>
        </div>
        
        <div class="chart-container">
          <div ref="chartRef" class="chart"></div>
        </div>

        <!-- 分组统计 -->
        <div class="group-stats">
          <h4>
            <el-icon><Collection /></el-icon>
            分组签到情况
          </h4>
          <div class="group-list">
            <div 
              v-for="group in groupStats" 
              :key="group.group_name"
              class="group-item"
            >
              <div class="group-info">
                <div class="group-name">{{ group.group_name }}</div>
                <div class="group-count">{{ group.checked_in }}/{{ group.total }}</div>
              </div>
              <div class="group-progress">
                <div class="group-progress-bar">
                  <div 
                    class="group-progress-fill"
                    :style="{ 
                      width: (group.total > 0 ? (group.checked_in / group.total * 100) : 0) + '%',
                      backgroundColor: getGroupColor(group.group_name)
                    }"
                  ></div>
                </div>
                <div class="group-percentage">
                  {{ group.total > 0 ? Math.round(group.checked_in / group.total * 100) : 0 }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部滚动横幅 -->
    <div class="bottom-banner">
      <div class="banner-content">
        <div class="banner-text">
          🎉 欢迎参加联盟杯内训师大赛！请各位参赛者及时签到，比赛即将开始！祝愿所有参赛者取得优异成绩！
        </div>
      </div>
    </div>

    <!-- 全屏切换按钮 -->
    <div class="fullscreen-btn" @click="toggleFullscreen">
      <el-icon><FullScreen /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

// 响应式数据
const currentTime = ref('')
const currentDate = ref('')
const isRefreshing = ref(false)
const chartRef = ref()

const stats = ref({
  totalParticipants: 0,
  checkedIn: 0
})

const recentCheckins = ref([])
const groupStats = ref([])

// 计算属性
const checkinProgress = computed(() => {
  if (stats.value.totalParticipants === 0) return 0
  return Math.round((stats.value.checkedIn / stats.value.totalParticipants) * 100)
})

// API配置
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 方法
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

const loadData = async () => {
  try {
    isRefreshing.value = true

    // 加载统计数据
    const statsRes = await api.get('/statistics/checkin')
    stats.value = {
      totalParticipants: statsRes.data.total_participants || 0,
      checkedIn: statsRes.data.checked_in || 0
    }

    // 加载最新签到记录
    const checkinsRes = await api.get('/checkins/recent?limit=10')
    recentCheckins.value = checkinsRes.data || []

    // 加载分组统计
    const groupsRes = await api.get('/statistics/groups')
    groupStats.value = groupsRes.data || []

    // 更新图表
    updateChart()
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    setTimeout(() => {
      isRefreshing.value = false
    }, 500)
  }
}

const updateChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  // 生成时间轴数据（最近24小时）
  const hours = []
  const checkinData = []
  const now = new Date()
  
  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000)
    hours.push(time.getHours() + ':00')
    // 模拟数据，实际应该从API获取
    checkinData.push(Math.floor(Math.random() * 20))
  }

  const option = {
    title: {
      text: '24小时签到趋势',
      left: 'center',
      textStyle: {
        color: '#2c3e50',
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.8)',
      textStyle: {
        color: '#fff'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours,
      axisLine: {
        lineStyle: {
          color: '#e0e6ed'
        }
      },
      axisLabel: {
        color: '#7f8c8d'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#e0e6ed'
        }
      },
      axisLabel: {
        color: '#7f8c8d'
      },
      splitLine: {
        lineStyle: {
          color: '#f5f7fa'
        }
      }
    },
    series: [
      {
        name: '签到人数',
        type: 'line',
        smooth: true,
        data: checkinData,
        lineStyle: {
          color: '#667eea',
          width: 3
        },
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
            ]
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

const formatTime = (timeString: string) => {
  if (!timeString) return ''
  const time = new Date(timeString)
  return time.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const getGroupColor = (groupName: string) => {
  const colors = [
    '#667eea', '#764ba2', '#67C23A', '#E6A23C', 
    '#F56C6C', '#909399', '#409EFF', '#36CFC9'
  ]
  const index = groupName.charCodeAt(0) % colors.length
  return colors[index]
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 定时器
let timeInterval: number
let dataInterval: number

// 生命周期
onMounted(async () => {
  // 更新时间
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  // 加载数据
  await loadData()
  dataInterval = setInterval(loadData, 10000) // 每10秒刷新一次
  
  // 初始化图表
  await nextTick()
  updateChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (chartRef.value) {
      const chart = echarts.getInstanceByDom(chartRef.value)
      chart?.resize()
    }
  })
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
})
</script>

<style scoped>
.display-checkin {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  overflow: hidden;
}

.display-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 40px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1800px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-icon {
  font-size: 48px;
  color: #FFD700;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
}

.main-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.sub-title {
  font-size: 18px;
  opacity: 0.9;
  margin: 5px 0 0 0;
}

.time-section {
  text-align: right;
}

.current-time {
  font-size: 32px;
  font-weight: bold;
  font-family: 'Courier New', monospace;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.current-date {
  font-size: 16px;
  opacity: 0.9;
  margin-top: 5px;
}

.stats-section {
  padding: 30px 40px;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1800px;
  margin: 0 auto;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 48px;
  margin-bottom: 20px;
  color: #FFD700;
}

.stat-number {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.stat-label {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.stat-progress {
  position: relative;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease;
}

.total-fill {
  background: linear-gradient(90deg, #FFD700, #FFA500);
}

.checkin-fill {
  background: linear-gradient(90deg, #67C23A, #85ce61);
}

.pending-fill {
  background: linear-gradient(90deg, #E6A23C, #f0a020);
}

.progress-text {
  position: absolute;
  top: -25px;
  right: 0;
  font-size: 14px;
  font-weight: bold;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  padding: 0 40px 30px;
  max-width: 1800px;
  margin: 0 auto;
}

.left-panel, .right-panel {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
  font-size: 20px;
  font-weight: bold;
}

.refresh-indicator {
  margin-left: auto;
  transition: transform 0.5s ease;
}

.refresh-indicator.active {
  transform: rotate(360deg);
}

.recent-checkins {
  max-height: 400px;
  overflow-y: auto;
}

.checkin-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
}

.checkin-avatar {
  position: relative;
}

.checkin-status {
  position: absolute;
  bottom: -2px;
  right: -2px;
  background: #67C23A;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
}

.checkin-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.checkin-org {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.checkin-time {
  font-size: 12px;
  opacity: 0.7;
}

.checkin-animation {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
}

.success-ripple {
  width: 40px;
  height: 40px;
  border: 2px solid #67C23A;
  border-radius: 50%;
  opacity: 0.6;
  animation: ripple 2s infinite;
}

.empty-checkins {
  text-align: center;
  padding: 60px 20px;
  opacity: 0.7;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.chart-container {
  height: 300px;
  margin-bottom: 30px;
}

.chart {
  width: 100%;
  height: 100%;
}

.group-stats h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 16px;
}

.group-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.group-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.group-count {
  font-size: 14px;
  opacity: 0.8;
}

.group-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 120px;
}

.group-progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.group-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease;
}

.group-percentage {
  font-size: 12px;
  font-weight: bold;
  min-width: 35px;
}

.bottom-banner {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px 0;
  overflow: hidden;
}

.banner-content {
  white-space: nowrap;
  animation: scroll 30s linear infinite;
}

.banner-text {
  font-size: 18px;
  font-weight: 500;
}

@keyframes scroll {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}

@keyframes ripple {
  0% {
    transform: scale(0.8);
    opacity: 0.6;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

.checkin-item-enter-active {
  transition: all 0.5s ease;
}

.checkin-item-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fullscreen-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.fullscreen-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .display-header {
    padding: 15px 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .main-title {
    font-size: 28px;
  }
  
  .current-time {
    font-size: 24px;
  }
}
</style>