<template>
  <div class="participant-management">
    <div class="page-header">
      <h1>参赛者管理</h1>
      <div class="header-actions">
        <el-button type="success" @click="exportData">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加参赛者
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchForm.name"
            placeholder="搜索姓名"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="searchForm.organization"
            placeholder="选择单位"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="org in organizations"
              :key="org"
              :label="org"
              :value="org"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="searchForm.group_id"
            placeholder="选择分组"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="searchForm.checkin_status"
            placeholder="签到状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="已签到" value="checked_in" />
            <el-option label="未签到" value="not_checked_in" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ totalCount }}</div>
            <div class="stat-label">总参赛者</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ checkedInCount }}</div>
            <div class="stat-label">已签到</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ ((checkedInCount / totalCount) * 100).toFixed(1) }}%</div>
            <div class="stat-label">签到率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ groups.length }}</div>
            <div class="stat-label">分组数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 参赛者列表 -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="filteredParticipants"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="照片" width="80">
          <template #default="{ row }">
            <el-avatar
              :size="50"
              :src="row.photo_path"
              :alt="row.name"
            >
              {{ row.name.charAt(0) }}
            </el-avatar>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="姓名" width="120" />
        
        <el-table-column prop="organization" label="单位" width="150" />
        
        <el-table-column prop="phone" label="手机号" width="130">
          <template #default="{ row }">
            {{ formatPhone(row.phone) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="group_name" label="分组" width="100" />
        
        <el-table-column label="签到状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row.is_checked_in ? 'success' : 'warning'"
              size="small"
            >
              {{ row.is_checked_in ? '已签到' : '未签到' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="签到时间" width="160">
          <template #default="{ row }">
            {{ row.checkin_time ? formatTime(row.checkin_time) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="showQRCode(row)"
            >
              二维码
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="editParticipant(row)"
            >
              编辑
            </el-button>
            <el-button
              type="text"
              size="small"
              style="color: #f56c6c"
              @click="deleteParticipant(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑参赛者对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingParticipant ? '编辑参赛者' : '添加参赛者'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="participantFormRef"
        :model="participantForm"
        :rules="participantRules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="participantForm.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="单位" prop="organization">
          <el-input v-model="participantForm.organization" placeholder="请输入单位" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="participantForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="分组" prop="group_id">
          <el-select v-model="participantForm.group_id" placeholder="选择分组">
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="照片">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :http-request="handleAvatarUpload"
          >
            <img v-if="participantForm.photo_path" :src="participantForm.photo_path" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveParticipant" :loading="saving">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 二维码对话框 -->
    <el-dialog
      v-model="showQRDialog"
      title="参赛者二维码"
      width="400px"
      align-center
    >
      <div v-if="currentQRCode" class="qr-code-container">
        <div class="participant-info">
          <h3>{{ currentQRCode.name }}</h3>
          <p>{{ currentQRCode.organization }}</p>
          <p>{{ currentQRCode.group_name }}</p>
        </div>
        <div class="qr-code-image">
          <img :src="currentQRCode.qr_code_data" alt="签到二维码" />
        </div>
        <div class="qr-code-url">
          <el-input
            :value="currentQRCode.checkin_url"
            readonly
            size="small"
          >
            <template #append>
              <el-button @click="copyUrl(currentQRCode.checkin_url)">复制</el-button>
            </template>
          </el-input>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="downloadQRCode">下载二维码</el-button>
        <el-button type="primary" @click="showQRDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElForm } from 'element-plus'
import { Search, Download, Plus } from '@element-plus/icons-vue'
import { participantsApi } from '@/api/participants'
import { groupsApi } from '@/api/groups'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showQRDialog = ref(false)
const editingParticipant = ref<any>(null)
const currentQRCode = ref<any>(null)
const participants = ref<any[]>([])
const groups = ref<any[]>([])
const selectedParticipants = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = reactive({
  name: '',
  organization: '',
  group_id: null,
  checkin_status: ''
})

const participantForm = reactive({
  name: '',
  organization: '',
  phone: '',
  group_id: null,
  photo_path: ''
})

const participantFormRef = ref<InstanceType<typeof ElForm>>()

// 表单验证规则
const participantRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  organization: [
    { required: true, message: '请输入单位', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  group_id: [
    { required: true, message: '请选择分组', trigger: 'change' }
  ]
}

// 计算属性
const organizations = computed(() => {
  const orgs = [...new Set(participants.value.map(p => p.organization))]
  return orgs.filter(Boolean)
})

const filteredParticipants = computed(() => {
  let filtered = participants.value

  if (searchForm.name) {
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(searchForm.name.toLowerCase())
    )
  }

  if (searchForm.organization) {
    filtered = filtered.filter(p => p.organization === searchForm.organization)
  }

  if (searchForm.group_id) {
    filtered = filtered.filter(p => p.group_id === searchForm.group_id)
  }

  if (searchForm.checkin_status) {
    const isCheckedIn = searchForm.checkin_status === 'checked_in'
    filtered = filtered.filter(p => p.is_checked_in === isCheckedIn)
  }

  return filtered
})

const totalCount = computed(() => filteredParticipants.value.length)
const checkedInCount = computed(() => 
  filteredParticipants.value.filter(p => p.is_checked_in).length
)

// 方法
const loadParticipants = async () => {
  try {
    loading.value = true
    const result = await participantsApi.getList()
    participants.value = result.items || []
  } catch (error) {
    console.error('加载参赛者失败:', error)
    ElMessage.error('加载参赛者失败')
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  try {
    const result = await groupsApi.getList()
    groups.value = result || []
  } catch (error) {
    console.error('加载分组失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection: any[]) => {
  selectedParticipants.value = selection
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const editParticipant = (participant: any) => {
  editingParticipant.value = participant
  Object.assign(participantForm, {
    name: participant.name,
    organization: participant.organization,
    phone: participant.phone,
    group_id: participant.group_id,
    photo_path: participant.photo_path || ''
  })
  showAddDialog.value = true
}

const resetForm = () => {
  editingParticipant.value = null
  Object.assign(participantForm, {
    name: '',
    organization: '',
    phone: '',
    group_id: null,
    photo_path: ''
  })
  if (participantFormRef.value) {
    participantFormRef.value.clearValidate()
  }
}

const saveParticipant = async () => {
  if (!participantFormRef.value) return

  try {
    await participantFormRef.value.validate()
    saving.value = true

    if (editingParticipant.value) {
      // 编辑模式
      await participantsApi.update(editingParticipant.value.id, participantForm)
      ElMessage.success('更新成功')
    } else {
      // 添加模式
      await participantsApi.create(participantForm)
      ElMessage.success('添加成功')
    }

    showAddDialog.value = false
    await loadParticipants()
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const deleteParticipant = async (participant: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除参赛者 "${participant.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await participantsApi.delete(participant.id)
    ElMessage.success('删除成功')
    await loadParticipants()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const showQRCode = async (participant: any) => {
  try {
    const qrData = await participantsApi.getQRCode(participant.id)
    currentQRCode.value = {
      ...participant,
      ...qrData
    }
    showQRDialog.value = true
  } catch (error) {
    console.error('获取二维码失败:', error)
    ElMessage.error('获取二维码失败')
  }
}

const copyUrl = async (url: string) => {
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadQRCode = () => {
  if (!currentQRCode.value) return
  
  const link = document.createElement('a')
  link.href = currentQRCode.value.qr_code_data
  link.download = `${currentQRCode.value.name}_签到二维码.png`
  link.click()
}

const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleAvatarUpload = (options: any) => {
  const file = options.file
  const reader = new FileReader()
  reader.onload = (e) => {
    participantForm.photo_path = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

const formatPhone = (phone: string) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1****$3')
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadParticipants()
  loadGroups()
})
</script>

<style scoped>
.participant-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card .el-card__body {
  padding: 20px;
  text-align: center;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.qr-code-container {
  text-align: center;
}

.participant-info {
  margin-bottom: 20px;
}

.participant-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.participant-info p {
  margin: 4px 0;
  color: #909399;
}

.qr-code-image {
  margin-bottom: 20px;
}

.qr-code-image img {
  max-width: 200px;
  height: auto;
}

.qr-code-url {
  margin-top: 16px;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 6px;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: 0.2s;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .participant-management {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .header-actions {
    justify-content: center;
  }
}
</style>