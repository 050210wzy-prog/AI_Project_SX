<template>
  <div class="academic-page">
    <section class="page-head">
      <div>
        <p class="eyebrow">ACADEMIC OFFICE</p>
        <h1>教务管理</h1>
        <p>24人工智能班课表按第1周到第18周查看，课程分布与移动端教务系统保持一致。</p>
      </div>
      <div class="head-actions">
        <el-button type="primary" @click="publishSchedule">发布本周课表</el-button>
      </div>
    </section>

    <section class="toolbar-band">
      <div class="control-group">
        <label>班级</label>
        <el-select v-model="selectedClass" filterable placeholder="选择班级" @change="loadGrades">
          <el-option v-for="item in classes" :key="item" :label="item" :value="item" />
        </el-select>
      </div>
      <div class="control-group week-control">
        <label>教学周</label>
        <div class="week-picker">
          <el-button @click="changeWeek(-1)">上一周</el-button>
          <el-select v-model="selectedWeek" filterable>
            <el-option v-for="week in 18" :key="week" :label="`第${week}周`" :value="week" />
          </el-select>
          <el-button @click="changeWeek(1)">下一周</el-button>
        </div>
      </div>
      <div class="control-group">
        <label>课程</label>
        <el-select v-model="selectedCourse" filterable allow-create default-first-option placeholder="选择或输入课程" @change="loadGrades">
          <el-option v-for="item in courseOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </div>
      <div class="toolbar-actions">
        <el-button @click="openScheduleDialog()">新增排课</el-button>
        <el-button type="success" @click="syncGrades">同步班级学生</el-button>
      </div>
    </section>

    <section class="summary-grid">
      <div class="metric-card"><span>当前班级</span><strong>{{ selectedClass || '未选择' }}</strong><small>{{ classStudents.length }} 名学生</small></div>
      <div class="metric-card"><span>教学周</span><strong>第{{ selectedWeek }}周</strong><small>{{ weekRangeText }}</small></div>
      <div class="metric-card"><span>本周课程</span><strong>{{ filteredSchedules.length }}</strong><small>每周分布一致</small></div>
      <div class="metric-card"><span>需关注</span><strong>{{ warningCount }}</strong><small>成绩或出勤异常</small></div>
    </section>

    <section class="schedule-section">
      <div class="schedule-title">
        <div>
          <p class="semester">2025-2026学年第二学期</p>
          <h2>第{{ selectedWeek }}周课表</h2>
        </div>
        <span class="week-range">{{ weekRangeText }}</span>
      </div>

      <div class="timetable-wrap">
        <div class="timetable">
          <div class="corner-cell">节次</div>
          <div v-for="day in weekDays" :key="day.key" class="day-head">
            <strong>{{ day.label }}</strong>
            <span>{{ day.date }}</span>
          </div>
          <template v-for="period in periods" :key="period">
            <div class="period-cell">{{ period }}</div>
            <div v-for="day in weekDays" :key="`${day.key}-${period}`" class="lesson-cell">
              <button
                v-if="lessonAt(day.label, period)"
                class="lesson-card"
                :class="`tone-${lessonTone(lessonAt(day.label, period))}`"
                :style="{ '--span': lessonSpan(lessonAt(day.label, period)) }"
                @click="openCourseDetail(lessonAt(day.label, period))"
              >
                <strong>{{ lessonAt(day.label, period).course }}</strong>
                <span>{{ lessonAt(day.label, period).teacher || '待分配' }}</span>
                <em>{{ lessonAt(day.label, period).room || '待定教室' }}</em>
              </button>
            </div>
          </template>
        </div>
      </div>
    </section>

    <section class="content-grid">
      <div class="work-panel">
        <div class="panel-head">
          <div><p class="eyebrow">SCHEDULE</p><h3>排课清单</h3></div>
          <el-tag type="info">{{ filteredSchedules.length }} 条</el-tag>
        </div>
        <el-table :data="filteredSchedules" stripe>
          <el-table-column prop="day" label="星期" width="72" />
          <el-table-column prop="time" label="节次" width="92" />
          <el-table-column prop="course" label="课程" min-width="150" />
          <el-table-column prop="teacher" label="教师" width="100" />
          <el-table-column prop="room" label="教室" width="140" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openScheduleDialog(row)">编辑</el-button>
              <el-button link @click="markAttendance(row)">考勤</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="work-panel">
        <div class="panel-head">
          <div><p class="eyebrow">ASSESSMENT</p><h3>成绩与考核</h3></div>
          <el-button @click="exportGrades">导出</el-button>
        </div>
        <el-table :data="grades" stripe>
          <el-table-column prop="examNo" label="考生号" min-width="132" />
          <el-table-column prop="student" label="姓名" width="90" />
          <el-table-column prop="course" label="课程" min-width="140" show-overflow-tooltip />
          <el-table-column label="平时分" width="126"><template #default="{ row }"><el-input-number v-model="row.processScore" :min="0" :max="100" size="small" /></template></el-table-column>
          <el-table-column label="期末分" width="126"><template #default="{ row }"><el-input-number v-model="row.finalScore" :min="0" :max="100" size="small" /></template></el-table-column>
          <el-table-column label="实训分" width="126"><template #default="{ row }"><el-input-number v-model="row.practiceScore" :min="0" :max="100" size="small" /></template></el-table-column>
          <el-table-column label="总评" width="96"><template #default="{ row }"><strong class="score-pill" :class="{ danger: previewTotal(row) < 60 }">{{ previewTotal(row) }}</strong></template></el-table-column>
          <el-table-column label="操作" width="88" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="saveGrade(row)">保存</el-button></template></el-table-column>
        </el-table>
      </div>
    </section>

    <el-dialog v-model="scheduleDialogVisible" :title="editingSchedule?.id ? '编辑排课' : '新增排课'" width="520px">
      <el-form :model="scheduleForm" label-width="84px">
        <el-form-item label="班级"><el-select v-model="scheduleForm.class_name" filterable><el-option v-for="item in classes" :key="item" :label="item" :value="item" /></el-select></el-form-item>
        <el-form-item label="星期"><el-select v-model="scheduleForm.day"><el-option v-for="day in dayLabels" :key="day" :label="day" :value="day" /></el-select></el-form-item>
        <el-form-item label="节次"><el-select v-model="scheduleForm.time" allow-create filterable><el-option v-for="item in timeOptions" :key="item" :label="item" :value="item" /></el-select></el-form-item>
        <el-form-item label="课程"><el-select v-model="scheduleForm.course" allow-create filterable><el-option v-for="item in courseOptions" :key="item" :label="item" :value="item" /></el-select></el-form-item>
        <el-form-item label="教师"><el-input v-model="scheduleForm.teacher" /></el-form-item>
        <el-form-item label="教室"><el-input v-model="scheduleForm.room" /></el-form-item>
        <el-form-item label="状态"><el-radio-group v-model="scheduleForm.status"><el-radio-button label="草稿" /><el-radio-button label="已发布" /></el-radio-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="scheduleDialogVisible = false">取消</el-button><el-button type="primary" @click="saveSchedule">保存排课</el-button></template>
    </el-dialog>

    <el-dialog v-model="attendanceDialogVisible" title="考勤点名" width="860px">
      <div v-if="attendanceSchedule" class="attendance-head">
        <div><h3>{{ attendanceSchedule.course }}</h3><p>{{ attendanceSchedule.className }} / 第{{ selectedWeek }}周 / {{ attendanceSchedule.day }} {{ attendanceSchedule.time }}</p></div>
        <el-tag type="info">{{ attendanceRows.length }} 人</el-tag>
      </div>
      <el-table :data="attendanceRows" stripe>
        <el-table-column prop="examNo" label="考生号" min-width="132" />
        <el-table-column prop="student" label="姓名" width="100" />
        <el-table-column label="考勤状态" width="260">
          <template #default="{ row }">
            <el-radio-group v-model="row.status" size="small" @change="saveAttendance(row)">
              <el-radio-button label="已到" />
              <el-radio-button label="迟到" />
              <el-radio-button label="请假" />
              <el-radio-button label="旷课" />
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="180"><template #default="{ row }"><el-input v-model="row.remark" size="small" @change="saveAttendance(row)" /></template></el-table-column>
      </el-table>
      <template #footer><el-button @click="attendanceDialogVisible = false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const dayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const periods = Array.from({ length: 12 }, (_, index) => index + 1)
const timeOptions = ['1-2节', '1-4节', '3-4节', '5-8节', '9-12节']
const defaultCourses = ['Python数据分析', '深度学习框架技术', '习近平新时代中国特色社会主义思想概论', '人工智能应用开发技术', '自然语言处理', '体育与健康4', '礼仪与沟通技巧', '数据结构']
const termStart = new Date(2026, 2, 2)

const selectedWeek = ref(1)
const classes = ref([])
const students = ref([])
const schedules = ref([])
const grades = ref([])
const courseOptions = ref([...defaultCourses])
const selectedClass = ref('')
const selectedCourse = ref(defaultCourses[0])
const scheduleDialogVisible = ref(false)
const attendanceDialogVisible = ref(false)
const editingSchedule = ref(null)
const attendanceSchedule = ref(null)
const attendanceRows = ref([])
const scheduleForm = reactive({ day: '周一', time: '1-4节', course: '', teacher: '', room: '', class_name: '', status: '草稿' })

const weekDays = computed(() => {
  const start = new Date(termStart)
  start.setDate(termStart.getDate() + (selectedWeek.value - 1) * 7)
  return dayLabels.map((label, index) => {
    const date = new Date(start)
    date.setDate(start.getDate() + index)
    return { key: label, label, date: `${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}` }
  })
})
const weekRangeText = computed(() => `${weekDays.value[0].date} - ${weekDays.value[6].date}`)
const classStudents = computed(() => students.value.filter((item) => item.className === selectedClass.value))
const filteredSchedules = computed(() => schedules.value.filter((item) => !selectedClass.value || item.className === selectedClass.value))
const warningCount = computed(() => grades.value.filter((item) => Number(item.totalScore || item.score || 0) < 60 || Number(item.attendance || 0) < 80).length)

function changeWeek(step) { selectedWeek.value = Math.min(18, Math.max(1, selectedWeek.value + step)) }
function previewTotal(row) {
  const process = Number(row.processScore || 0)
  const final = Number(row.finalScore || 0)
  const practice = Number(row.practiceScore || 0)
  return Math.round(Math.max(0, Math.min(100, process * 0.3 + final * 0.5 + practice * 0.2)) * 10) / 10
}
function parseTimeRange(timeText = '') {
  const match = String(timeText).match(/(\d+)\D+(\d+)/)
  if (!match) return { start: 1, end: 1 }
  return { start: Number(match[1]), end: Number(match[2]) }
}
function lessonAt(day, period) {
  return filteredSchedules.value.find((item) => {
    const range = parseTimeRange(item.time)
    return item.day === day && range.start === period
  })
}
function lessonSpan(item) {
  if (!item) return 1
  const range = parseTimeRange(item.time)
  return Math.max(1, range.end - range.start + 1)
}
function lessonTone(item) { return (courseOptions.value.indexOf(item?.course) % 8) + 1 }
function openCourseDetail(row) { openScheduleDialog(row) }
async function loadMeta() {
  const [{ data: meta }, { data: studentRows }] = await Promise.all([http.get('/admin/academic/classes'), http.get('/admin/students')])
  students.value = studentRows
  classes.value = [...new Set([...(meta.classes || []), ...studentRows.map((item) => item.className).filter(Boolean), '24人工智能班'])]
  courseOptions.value = [...new Set([...defaultCourses, ...(meta.courses || [])])]
  selectedClass.value = selectedClass.value || classes.value.find((item) => item === '24人工智能班') || classes.value.find((item) => item.includes('人工智能')) || classes.value[0] || ''
}
async function loadSchedules() {
  const { data } = await http.get('/admin/academic/schedules')
  schedules.value = data
  courseOptions.value = [...new Set([...courseOptions.value, ...data.map((item) => item.course).filter(Boolean)])]
}
async function loadGrades() {
  if (!selectedClass.value || !selectedCourse.value) {
    grades.value = []
    return
  }
  const { data } = await http.get('/admin/academic/grades', { params: { class_name: selectedClass.value, course: selectedCourse.value } })
  grades.value = data
}
async function load() {
  await loadMeta()
  await loadSchedules()
  await loadGrades()
}
function openScheduleDialog(row) {
  editingSchedule.value = row || null
  Object.assign(scheduleForm, {
    day: row?.day || '周一',
    time: row?.time || '1-4节',
    course: row?.course || selectedCourse.value || '',
    teacher: row?.teacher || '',
    room: row?.room || '',
    class_name: row?.className || selectedClass.value || '',
    status: row?.status || '草稿'
  })
  scheduleDialogVisible.value = true
}
async function saveSchedule() {
  if (editingSchedule.value?.id) await http.put(`/admin/academic/schedules/${editingSchedule.value.id}`, scheduleForm)
  else await http.post('/admin/academic/schedules', scheduleForm)
  ElMessage.success('排课已保存')
  scheduleDialogVisible.value = false
  await loadSchedules()
  await loadGrades()
}
async function publishSchedule() {
  const { data } = await http.post('/admin/academic/schedules/publish')
  ElMessage.success(`课表已发布：${data.count} 条`)
  await loadSchedules()
}
async function markAttendance(row) {
  attendanceSchedule.value = row
  const { data } = await http.get(`/admin/academic/schedules/${row.id}/attendance`, { params: { week: selectedWeek.value } })
  attendanceRows.value = data
  attendanceDialogVisible.value = true
}
async function saveAttendance(row) {
  await http.put(`/admin/academic/attendance/${row.id}`, { status: row.status, remark: row.remark })
}
async function syncGrades() {
  if (!selectedClass.value || !selectedCourse.value) {
    ElMessage.warning('请先选择班级和课程')
    return
  }
  const { data } = await http.post('/admin/academic/grades/sync', { class_name: selectedClass.value, course: selectedCourse.value, assessment: '平时+期末' })
  ElMessage.success(`已同步 ${data.total} 名学生，新增 ${data.created} 条`)
  await loadGrades()
}
async function saveGrade(row) {
  await http.put(`/admin/academic/grades/${row.id}`, { process_score: row.processScore, final_score: row.finalScore, practice_score: row.practiceScore, attendance: row.attendance, assessment: row.assessment, status: row.status })
  ElMessage.success(`${row.student} 的成绩已保存`)
  await loadGrades()
}
function exportGrades() {
  const header = '考生号,姓名,班级,课程,总评,出勤率,状态'
  const lines = grades.value.map((item) => [item.examNo, item.student, item.className, item.course, item.totalScore, item.attendance, item.status].map((value) => `"${String(value ?? '').replaceAll('"', '""')}"`).join(','))
  const blob = new Blob([`\ufeff${[header, ...lines].join('\n')}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedClass.value || '班级'}-${selectedCourse.value || '课程'}-成绩考核.csv`
  a.click()
  URL.revokeObjectURL(url)
}
onMounted(load)
</script>

<style scoped>
.academic-page { color: #1f2a2f; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; padding: 28px; margin-bottom: 18px; border: 1px solid rgba(0,102,179,.12); border-radius: 8px; background: linear-gradient(135deg,#f8fbff 0%,#eef8f3 100%); }
.eyebrow,.semester { margin: 0 0 8px; color: #0066b3; font-size: 12px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
h1,h2,h3 { margin: 0; letter-spacing: 0; }
.page-head h1 { font-size: 34px; }
.page-head p { margin-bottom: 0; color: #5e6c75; }
.head-actions,.toolbar-actions,.panel-actions,.week-picker { display: flex; align-items: center; gap: 10px; }
.summary-grid { display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: 14px; margin-bottom: 18px; }
.metric-card { min-height: 104px; padding: 18px; border: 1px solid #e2eaf0; border-radius: 8px; background: #fff; }
.metric-card span,.metric-card small { display: block; color: #6d7b84; }
.metric-card strong { display: block; margin: 8px 0 4px; color: #003b6f; font-size: 28px; }
.toolbar-band { display: grid; grid-template-columns: minmax(180px,.8fr) minmax(340px,1.1fr) minmax(240px,1fr) auto; align-items: end; gap: 14px; padding: 16px; margin-bottom: 18px; border: 1px solid #e1e8ee; border-radius: 8px; background: #fff; }
.control-group { display: grid; gap: 6px; min-width: 0; }
.control-group label { color: #52616a; font-size: 13px; font-weight: 700; }
.schedule-section,.work-panel { margin-bottom: 18px; border: 1px solid #e1e8ee; border-radius: 8px; background: #fff; }
.schedule-title,.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 18px 20px; border-bottom: 1px solid #eef2f5; }
.week-range { color: #2e7d32; font-weight: 800; }
.timetable-wrap { overflow-x: auto; padding: 16px; }
.timetable { display: grid; grid-template-columns: 58px repeat(7,minmax(132px,1fr)); grid-template-rows: 68px repeat(12,46px); min-width: 980px; border: 1px solid #dde7ee; border-radius: 8px; overflow: hidden; background: #eef3f7; }
.corner-cell,.day-head,.period-cell,.lesson-cell { position: relative; border-right: 1px solid #dde7ee; border-bottom: 1px solid #dde7ee; background: #fff; }
.corner-cell,.period-cell { display: grid; place-items: center; color: #667680; font-weight: 800; }
.day-head { display: grid; place-items: center; gap: 2px; background: #f7fbff; }
.day-head strong { color: #12344d; font-size: 18px; }
.day-head span { color: #7c8a92; font-size: 13px; }
.lesson-card { position: absolute; z-index: 2; inset: 4px; height: calc(var(--span) * 46px - 8px); padding: 10px; border: 0; border-radius: 8px; color: #fff; text-align: left; cursor: pointer; box-shadow: 0 10px 24px rgba(21,54,81,.16); }
.lesson-card strong,.lesson-card span,.lesson-card em { display: block; overflow: hidden; text-overflow: ellipsis; }
.lesson-card strong { font-size: 15px; line-height: 1.32; }
.lesson-card span,.lesson-card em { margin-top: 5px; font-size: 12px; font-style: normal; opacity: .94; }
.tone-1 { background: linear-gradient(135deg,#667eea,#8fa2ff); } .tone-2 { background: linear-gradient(135deg,#2196d3,#62bef6); } .tone-3 { background: linear-gradient(135deg,#64c3bd,#a6e4dd); color: #174a55; } .tone-4 { background: linear-gradient(135deg,#3ca37f,#89d8bd); } .tone-5 { background: linear-gradient(135deg,#d6b64f,#f1dfa6); color: #5b4512; } .tone-6 { background: linear-gradient(135deg,#9aa0e8,#d5d8fa); } .tone-7 { background: linear-gradient(135deg,#8cc3e8,#d7ecfb); color: #24506b; } .tone-8 { background: linear-gradient(135deg,#e58f86,#f7d0cb); }
.content-grid { display: grid; grid-template-columns: minmax(0,.9fr) minmax(0,1.4fr); gap: 18px; }
.work-panel :deep(.el-table) { padding: 0 12px 12px; }
.score-pill { display: inline-grid; min-width: 52px; height: 28px; place-items: center; border-radius: 8px; background: #eef8f3; color: #2e7d32; }
.score-pill.danger { background: #fff1f1; color: #c41e3a; }
.attendance-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 14px; }
@media (max-width: 1180px) { .toolbar-band,.summary-grid,.content-grid { grid-template-columns: 1fr 1fr; } .content-grid { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .page-head,.schedule-title,.panel-head { align-items: stretch; flex-direction: column; } .toolbar-band,.summary-grid { grid-template-columns: 1fr; } .head-actions,.toolbar-actions,.week-picker { justify-content: flex-start; flex-wrap: wrap; } }
</style>
