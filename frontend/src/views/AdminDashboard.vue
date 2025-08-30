<template>
  <div class="admin-dashboard">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon class="logo-icon"><Trophy /></el-icon>
          <span class="logo-text">联盟杯内训师大赛管理系统</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button @click="exportData">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 统计卡片区域 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6" :md="6" :lg="6">
            <div class="stat-card total">
              <div class="stat-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.totalParticipants }}</div>
                <div class="stat-label">总参赛者</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6" :md="6" :lg="6">
            <div class="stat-card checkin">
              <div class="stat-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.checkedIn }}</div>
                <div class="stat-label">已签到</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6" :md="6" :lg="6">
            <div class="stat-card scored">
              <div class="stat-icon">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.totalScores }}</div>
                <div class="stat-label">评分数量</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6" :md="6" :lg="6">
            <div class="stat-card rate">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.checkinRate }}%</div>
                <div class="stat-label">签到率</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 功能区域 -->
      <el-row :gutter="20" class="function-section">
        <!-- 二维码区域 -->
        <el-col :xs="24" :sm="12" :md="8" :lg="8">
          <el-card class="qr-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><QrCode /></el-icon>
                <span>签到二维码</span>
              </div>
            </template>
            <div class="qr-content">
              <div class="qr-image-container" v-if="qrCodeData">
                <img :src="qrCodeData" alt="签到二维码" class="qr-image" />
              </div>
              <div class="qr-actions">
                <el-button type="primary" @click="generateQRCode" :loading="qrLoading">
                  {{ qrCodeData ? '刷新二维码' : '生成二维码' }}
                </el-button>
              </div>
              <div class="qr-links">
                <el-button text @click="openMobileCheckin">
                  <el-icon><Cellphone /></el-icon>
                  移动端签到
                </el-button>
                <el-button text @click="openJudgeScore">
                  <el-icon><User /></el-icon>
                  评委打分
                </el-button>
                <el-button text @click="openDisplayScreen">
                  <el-icon><Monitor /></el-icon>
                  大屏展示
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 实时图表 -->
        <el-col :xs="24" :sm="12" :md="16" :lg="16">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>签到统计</span>
              </div>
            </template>
            <div class="chart-container">
              <div ref="chartRef" class="chart"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 参赛者列表 -->
      <el-card class="participants-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><UserFilled /></el-icon>
            <span>参赛者管理</span>
            <div class="header-actions">
              <el-input
                v-model="searchText"
                placeholder="搜索参赛者..."
                style="width: 200px"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="filteredParticipants" 
          style="width: 100%" 
          :loading="tableLoading"
          stripe
        >
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="organization" label="单位" width="200" />
          <el-table-column prop="group_name" label="分组" width="120" />
          <el-table-column prop="phone" label="手机号" width="130" />
          <el-table-column label="签到状态" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.is_checked_in ? 'success' : 'info'">
                {{ scope.row.is_checked_in ? '已签到' : '未签到' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="checkin_time" label="签到时间" width="180">
            <template #default="scope">
              {{ scope.row.checkin_time ? formatTime(scope.row.checkin_time) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="评分状态" width="120">
            <template #default="scope">
              <el-tag :type="scope.row.score_count > 0 ? 'success' : 'warning'">
                {{ scope.row.score_count || 0 }}分
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="150">
            <template #default="scope">
              <el-button 
                size="small" 
                type="primary" 
                @click="viewParticipant(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const stats = ref({
  totalParticipants: 0,
  checkedIn: 0,
  totalScores: 0,
  checkinRate: 0
})

const participants = ref([])
const searchText = ref('')
const qrCodeData = ref('')
const qrLoading = ref(false)
const tableLoading = ref(false)
const chartRef = ref()

// API配置
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// 计算属性
const filteredParticipants = computed(() => {
  if (!searchText.value) return participants.value
  return participants.value.filter(p => 
    p.name.includes(searchText.value) || 
    p.organization.includes(searchText.value)
  )
})

// 方法
const loadData = async () => {
  try {
    tableLoading.value = true
    
    // 加载参赛者数据
    const participantsRes = await api.get('/participants')
    participants.value = participantsRes.data

    // 加载统计数据
    const checkinRes = await api.get('/statistics/checkin')
    const scoresRes = await api.get('/statistics/scores')
    
    stats.value = {
      totalParticipants: checkinRes.data.total_participants || 0,
      checkedIn: checkinRes.data.checked_in || 0,
      totalScores: scoresRes.data.total_scores || 0,
      checkinRate: checkinRes.data.checkin_rate || 0
    }

    // 更新图表
    updateChart()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    tableLoading.value = false
  }
}

const generateQRCode = async () => {
  try {
    qrLoading.value = true
    const response = await api.get('/qrcode/public')
    qrCodeData.value = response.data.qr_code_data
    ElMessage.success('二维码生成成功')
  } catch (error) {
    console.error('生成二维码失败:', error)
    ElMessage.error('生成二维码失败')
  } finally {
    qrLoading.value = false
  }
}

const updateChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  const option = {
    title: {
      text: '签到进度',
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '签到统计',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '60%'],
        data: [
          { value: stats.value.checkedIn, name: '已签到', itemStyle: { color: '#67C23A' } },
          { value: stats.value.totalParticipants - stats.value.checkedIn, name: '未签到', itemStyle: { color: '#E6A23C' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  chart.setOption(option)
}

const refreshData = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

const exportData = async () => {
  try {
    const result = await ElMessageBox.confirm(
      '确定要导出所有数据吗？',
      '导出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    if (result === 'confirm') {
      // 这里实现导出逻辑
      ElMessage.success('导出功能开发中...')
    }
  } catch {
    // 用户取消
  }
}

const viewParticipant = async (participant: any) => {
  try {
    const response = await api.get(`/participants/${participant.id}/detail`)
    const detail = response.data
    
    // 使用Element Plus的消息框显示详细信息
    const h = ElMessageBox
    await ElMessageBox({
      title: `参赛者详情 - ${detail.name}`,
      message: h('div', { class: 'participant-detail' }, [
        h('div', { class: 'detail-section' }, [
          h('h4', '基本信息'),
          h('p', `姓名: ${detail.name}`),
          h('p', `单位: ${detail.organization}`),
          h('p', `手机: ${detail.phone}`),
          h('p', `分组: ${detail.group_name}`),
        ]),
        h('div', { class: 'detail-section' }, [
          h('h4', '签到信息'),
          h('p', `签到状态: ${detail.is_checked_in ? '已签到' : '未签到'}`),
          h('p', `签到时间: ${detail.checkin_time ? formatTime(detail.checkin_time) : '未签到'}`),
        ]),
        h('div', { class: 'detail-section' }, [
          h('h4', '评分信息'),
          h('p', `评分次数: ${detail.score_count}`),
          h('p', `平均分: ${detail.avg_score} 分`),
        ]),
        detail.scores.length > 0 && h('div', { class: 'detail-section' }, [
          h('h4', '详细评分'),
          ...detail.scores.map(score => 
            h('p', `${score.judge_name}: ${score.score} 分 (${formatTime(score.created_at)})`)
          )
        ])
      ]),
      confirmButtonText: '关闭',
      showCancelButton: false,
      customClass: 'participant-detail-dialog'
    })
  } catch (error) {
    console.error('获取参赛者详情失败:', error)
    ElMessage.error('获取参赛者详情失败')
  }
}

const openMobileCheckin = () => {
  window.open('/mobile/checkin', '_blank')
}

const openJudgeScore = () => {
  window.open('/judge/score', '_blank')
}

const openDisplayScreen = () => {
  window.open('/display/checkin', '_blank')
}

const formatTime = (timeString: string) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(async () => {
  await loadData()
  await generateQRCode()
  
  // 初始化图表
  await nextTick()
  updateChart()
  
  // 定时刷新数据
  setInterval(loadData, 30000)
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0 20px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 32px;
  color: #667eea;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
}

.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
  height: 120px;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-card.checkin .stat-icon {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.stat-card.scored .stat-icon {
  background: linear-gradient(135deg, #E6A23C, #f0a020);
}

.stat-card.rate .stat-icon {
  background: linear-gradient(135deg, #F56C6C, #f78989);
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
}

.function-section {
  margin-bottom: 30px;
}

.qr-card, .chart-card, .participants-card {
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.qr-content {
  text-align: center;
}

.qr-image-container {
  margin-bottom: 20px;
}

.qr-image {
  width: 200px;
  height: 200px;
  border-radius: 12px;
  border: 4px solid #f5f7fa;
}

.qr-actions {
  margin-bottom: 20px;
}

.qr-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-container {
  height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
}

.participants-card .card-header {
  justify-content: space-between;
}

/* 参赛者详情弹窗样式 */
:deep(.participant-detail-dialog) {
  width: 90%;
  max-width: 600px;
}

:deep(.participant-detail) {
  text-align: left;
}

:deep(.detail-section) {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

:deep(.detail-section h4) {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 2px solid #667eea;
  padding-bottom: 8px;
}

:deep(.detail-section p) {
  margin: 8px 0;
  color: #495057;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    height: auto;
    padding: 20px 0;
    gap: 20px;
  }

  .main-content {
    padding: 20px 10px;
  }

  .stat-card {
    padding: 16px;
    height: auto;
  }

  .stat-number {
    font-size: 24px;
  }
  
  :deep(.participant-detail-dialog) {
    width: 95%;
  }
}
</style>