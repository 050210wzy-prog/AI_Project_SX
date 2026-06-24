<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">STUDENT AFFAIRS</p>
        <h1>学生管理</h1>
        <p>覆盖学生档案、录取状态、班级专业分配、批量维护、通知公告和 Excel 导入导出。</p>
      </div>
      <div class="actions">
        <el-upload :show-file-list="false" accept=".xlsx" :http-request="importStudents">
          <el-button>导入 Excel</el-button>
        </el-upload>
        <el-button @click="exportStudents(filteredStudents)">导出当前结果</el-button>
        <el-button type="primary" @click="dialogVisible = true">新增学生</el-button>
      </div>
    </section>

    <el-row :gutter="16" class="stats">
      <el-col v-for="item in statCards" :key="item.label" :xs="12" :md="6">
        <el-card shadow="never" class="stat-card">
          <span>{{ item.label }}</span>
          <b>{{ item.value }}</b>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="panel">
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索姓名、考生号、学号、专业、班级、身份证号" />
        <el-select v-model="status" clearable placeholder="录取状态">
          <el-option label="已录取" value="已录取" />
          <el-option label="待确认" value="待确认" />
          <el-option label="已报到" value="已报到" />
          <el-option label="需补材料" value="需补材料" />
        </el-select>
        <el-button @click="reset">重置</el-button>
      </div>

      <div class="batchbar">
        <span>已选择 {{ selectedRows.length }} 人</span>
        <el-button :disabled="!selectedRows.length" @click="batchStatus('已报到')">设为已报到</el-button>
        <el-button :disabled="!selectedRows.length" @click="batchStatus('需补材料')">设为需补材料</el-button>
        <el-button :disabled="!selectedRows.length" @click="batchCounselor">批量辅导员</el-button>
        <el-button :disabled="!selectedRows.length" @click="exportStudents(selectedRows)">导出所选</el-button>
        <el-button :disabled="!selectedRows.length" type="danger" @click="batchDelete">批量删除</el-button>
      </div>

      <el-table :data="filteredStudents" stripe @selection-change="selectedRows = $event">
        <el-table-column type="selection" width="46" />
        <el-table-column prop="examNo" label="考生号" width="150" />
        <el-table-column prop="student_no" label="学号" width="110" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="major" label="录取专业" min-width="170" />
        <el-table-column prop="className" label="班级" width="130" />
        <el-table-column prop="score" label="投档成绩" width="100" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="counselor" label="辅导员" width="100" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/admin/students/${row.id}`)">档案</el-button>
            <el-button link @click="assignClass(row)">分班</el-button>
            <el-button link @click="sendNotice(row)">通知</el-button>
            <el-button link type="danger" @click="deleteStudent(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="panel">
      <h3>通知公告触达</h3>
      <el-timeline>
        <el-timeline-item v-for="item in notices" :key="item.title" :timestamp="item.time">
          <strong>{{ item.title }}</strong>
          <p>{{ item.content }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增学生档案" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="考生号"><el-input v-model="form.examNo" /></el-form-item>
        <el-form-item label="专业"><el-input v-model="form.major" /></el-form-item>
        <el-form-item label="班级"><el-input v-model="form.className" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addStudent">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const keyword = ref('')
const status = ref('')
const dialogVisible = ref(false)
const form = ref({ name: '', examNo: '', major: '', className: '', phone: '' })
const students = ref([])
const notices = ref([])
const selectedRows = ref([])

const filteredStudents = computed(() => {
  const key = keyword.value.trim()
  return students.value.filter((item) => {
    const values = [item.examNo, item.student_no, item.name, item.major, item.className, item.id_card]
    const hitKey = !key || values.some((value) => String(value || '').includes(key))
    const hitStatus = !status.value || item.status === status.value
    return hitKey && hitStatus
  })
})

const statCards = computed(() => [
  { label: '学生档案', value: students.value.length },
  { label: '已报到', value: students.value.filter((item) => item.status === '已报到').length },
  { label: '待确认', value: students.value.filter((item) => item.status === '待确认').length },
  { label: '需补材料', value: students.value.filter((item) => item.status === '需补材料').length }
])

const statusType = (value) => ({ 已报到: 'success', 已录取: 'primary', 待确认: 'warning', 需补材料: 'danger' }[value] || 'info')
const reset = () => {
  keyword.value = ''
  status.value = ''
}

function payloadFrom(row, patch = {}) {
  return {
    exam_no: row.examNo,
    name: row.name,
    major: row.major,
    class_name: row.className,
    phone: row.phone,
    status: row.status,
    counselor: row.counselor || '待分配',
    ...patch
  }
}

async function load() {
  const [studentRes, noticeRes] = await Promise.all([
    http.get('/admin/students'),
    http.get('/admin/admin-notices')
  ])
  students.value = studentRes.data
  notices.value = noticeRes.data
}
async function addStudent() {
  await http.post('/admin/students', {
    exam_no: form.value.examNo,
    name: form.value.name,
    major: form.value.major,
    class_name: form.value.className,
    phone: form.value.phone,
    status: '待确认',
    counselor: '待分配'
  })
  form.value = { name: '', examNo: '', major: '', className: '', phone: '' }
  dialogVisible.value = false
  ElMessage.success('学生档案已保存到数据库')
  await load()
}
async function importStudents(option) {
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const { data } = await http.post('/admin/students/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(`导入完成：新增 ${data.created} 人，更新 ${data.updated} 人，跳过 ${data.skipped} 行`)
    await load()
    option.onSuccess?.(data)
  } catch (error) {
    option.onError?.(error)
    ElMessage.error(error?.response?.data?.detail || '学生导入失败，请检查 Excel 表头')
  }
}
async function assignClass(row) {
  const nextClass = row.className || `${(row.major || '新生').slice(0, 2)}2501`
  await http.put(`/admin/students/${row.id}`, payloadFrom(row, { class_name: nextClass }))
  ElMessage.success(`${row.name} 分班信息已保存`)
  await load()
}
async function sendNotice(row) {
  await http.post(`/admin/students/${row.id}/notice`)
  ElMessage.success(`已向 ${row.name} 发送通知并记录`)
  await load()
}
async function deleteStudent(row) {
  await ElMessageBox.confirm(`确定删除 ${row.name} 的学生档案吗？此操作不可恢复。`, '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await http.delete(`/admin/students/${row.id}`)
  ElMessage.success(`${row.name} 已删除`)
  await load()
}
async function batchStatus(nextStatus) {
  await Promise.all(selectedRows.value.map((row) => http.put(`/admin/students/${row.id}`, payloadFrom(row, { status: nextStatus }))))
  ElMessage.success(`已更新 ${selectedRows.value.length} 名学生状态`)
  selectedRows.value = []
  await load()
}
async function batchCounselor() {
  const { value } = await ElMessageBox.prompt('请输入辅导员姓名', '批量设置辅导员', {
    confirmButtonText: '保存',
    cancelButtonText: '取消'
  })
  await Promise.all(selectedRows.value.map((row) => http.put(`/admin/students/${row.id}`, payloadFrom(row, { counselor: value || '待分配' }))))
  ElMessage.success(`已更新 ${selectedRows.value.length} 名学生辅导员`)
  selectedRows.value = []
  await load()
}
async function batchDelete() {
  await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 名学生吗？此操作不可恢复。`, '批量删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await Promise.all(selectedRows.value.map((row) => http.delete(`/admin/students/${row.id}`)))
  ElMessage.success(`已删除 ${selectedRows.value.length} 名学生`)
  selectedRows.value = []
  await load()
}
function exportStudents(rows) {
  const headers = ['考生号', '学号', '姓名', '性别', '身份证号', '出生年月', '省份', '城市', '院系', '班级', '录取专业', '录取方式', '录取批次', '科类', '投档成绩', '联系电话', '家庭地址', '状态', '辅导员']
  const dataRows = rows.map((s) => [s.examNo, s.student_no, s.name, s.gender, s.id_card, s.birthday, s.province, s.city, s.department, s.className, s.major, s.admission_type, s.admission_batch, s.subject || s.subject_name, s.score, s.phone, s.address, s.status, s.counselor])
  const escape = (value) => `"${String(value ?? '').replace(/"/g, '""')}"`
  const csv = [headers.map(escape).join(','), ...dataRows.map((row) => row.map(escape).join(','))].join('\n')
  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '学生档案.csv'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(load)
</script>

<style scoped>
.page-head,
.panel,
.stat-card {
  border-radius: 24px;
  border: 1px solid rgba(16, 23, 19, .1);
  background: rgba(255,255,255,.78);
}
.page-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 26px;
  margin-bottom: 18px;
}
.eyebrow {
  font-weight: 900;
  letter-spacing: .08em;
  font-size: 12px;
  margin: 0 0 8px;
}
h1 {
  margin: 0;
  font-size: 34px;
}
.page-head p {
  color: #66716d;
}
.actions,
.toolbar,
.batchbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.stats {
  margin-bottom: 18px;
}
.stat-card span {
  color: #66716d;
}
.stat-card b {
  display: block;
  font-size: 34px;
  margin-top: 8px;
}
.panel {
  margin-top: 18px;
}
.toolbar,
.batchbar {
  margin-bottom: 14px;
}
.toolbar .el-input {
  max-width: 420px;
}
.batchbar {
  padding: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}
</style>
