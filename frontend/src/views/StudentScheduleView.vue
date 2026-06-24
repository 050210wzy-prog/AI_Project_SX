<template>
  <div class="schedule-page">
    <header class="mobile-head">
      <button class="back-btn" @click="$router.push('/')">‹</button>
      <div>
        <p>教务系统</p>
        <h1>我的课表</h1>
      </div>
      <button v-if="studentToken" class="logout-btn" @click="logout">退出</button>
    </header>

    <main v-if="!studentToken" class="login-box">
      <el-card shadow="never">
        <h2>学生登录</h2>
        <p>使用学号登录，初始密码与学号一致。</p>
        <el-input v-model="loginForm.student_no" placeholder="请输入学号" />
        <el-input v-model="loginForm.password" type="password" show-password placeholder="请输入密码" />
        <el-button type="primary" size="large" :loading="loading" @click="studentLogin">登录查看</el-button>
      </el-card>
    </main>

    <main v-else class="schedule-shell">
      <section class="student-card">
        <div>
          <span>{{ student.name }}</span>
          <strong>{{ student.className }}</strong>
          <p>{{ student.major }} / 学号：{{ student.studentNo }} / 考生号：{{ student.examNo }}</p>
        </div>
        <el-tag type="success">已登录</el-tag>
      </section>

      <section class="week-bar">
        <el-button text @click="changeWeek(-1)">上一周</el-button>
        <div>
          <h2>第{{ selectedWeek }}周</h2>
          <p>2025-2026学年第二学期</p>
        </div>
        <el-button text @click="changeWeek(1)">下一周</el-button>
      </section>

      <section class="class-row">
        <el-select v-model="selectedWeek">
          <el-option v-for="week in 18" :key="week" :label="`第${week}周`" :value="week" />
        </el-select>
      </section>

      <section class="timetable-wrap">
        <div class="timetable">
          <div class="corner-cell"></div>
          <div v-for="day in weekDays" :key="day.key" class="day-head">
            <span>{{ day.date }}</span>
            <strong>{{ day.label }}</strong>
          </div>
          <template v-for="period in periods" :key="period">
            <div class="period-cell">{{ period }}</div>
            <div v-for="day in weekDays" :key="`${day.key}-${period}`" class="lesson-cell">
              <button
                v-if="lessonAt(day.label, period)"
                class="lesson-card"
                :class="`tone-${lessonTone(lessonAt(day.label, period))}`"
                :style="{ '--span': lessonSpan(lessonAt(day.label, period)) }"
                @click="openCourse(lessonAt(day.label, period))"
              >
                <strong>{{ lessonAt(day.label, period).course }}</strong>
                <span>{{ lessonAt(day.label, period).room }}</span>
              </button>
            </div>
          </template>
        </div>
      </section>

      <section class="grades-panel">
        <div class="panel-title">
          <h2>我的成绩与考勤</h2>
          <span>{{ grades.length }} 门课程</span>
        </div>
        <el-table :data="grades" stripe>
          <el-table-column prop="course" label="课程" min-width="150" />
          <el-table-column prop="totalScore" label="总评" width="80" />
          <el-table-column label="出勤率" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.attendance" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="assessment" label="考核方式" width="110" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === '正常' ? 'success' : 'warning'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </section>
    </main>

    <el-dialog v-model="courseVisible" title="课程详情" width="420px">
      <div v-if="selectedLesson" class="course-detail">
        <h3>{{ selectedLesson.course }}</h3>
        <p>第{{ selectedWeek }}周 / {{ selectedLesson.day }} {{ selectedLesson.time }}</p>
        <dl>
          <dt>班级</dt>
          <dd>{{ selectedLesson.className }}</dd>
          <dt>教师</dt>
          <dd>{{ selectedLesson.teacher || '待分配' }}</dd>
          <dt>地点</dt>
          <dd>{{ selectedLesson.room }}</dd>
          <dt>说明</dt>
          <dd>{{ courseDescription(selectedLesson.course) }}</dd>
        </dl>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import studentHttp from '../api/studentHttp'

const dayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const periods = Array.from({ length: 12 }, (_, index) => index + 1)
const termStart = new Date(2026, 2, 2)
const selectedWeek = ref(1)
const schedules = ref([])
const grades = ref([])
const student = ref({})
const studentToken = ref(localStorage.getItem('student_token') || '')
const loading = ref(false)
const courseVisible = ref(false)
const selectedLesson = ref(null)
const loginForm = reactive({ student_no: '', password: '' })

const weekDays = computed(() => {
  const start = new Date(termStart)
  start.setDate(termStart.getDate() + (selectedWeek.value - 1) * 7)
  return dayLabels.map((label, index) => {
    const date = new Date(start)
    date.setDate(start.getDate() + index)
    return {
      key: label,
      label,
      date: `${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
    }
  })
})

function changeWeek(step) {
  selectedWeek.value = Math.min(18, Math.max(1, selectedWeek.value + step))
}
function parseTimeRange(timeText = '') {
  const match = String(timeText).match(/(\d+)\D+(\d+)/)
  if (!match) return { start: 1, end: 1 }
  return { start: Number(match[1]), end: Number(match[2]) }
}
function lessonAt(day, period) {
  return schedules.value.find((item) => {
    const range = parseTimeRange(item.time)
    return item.day === day && range.start === period
  })
}
function lessonSpan(item) {
  const range = parseTimeRange(item?.time)
  return Math.max(1, range.end - range.start + 1)
}
function lessonTone(item) {
  const tones = {
    Python数据分析: 1,
    深度学习框架技术: 2,
    习近平新时代中国特色社会主义思想概论: 3,
    人工智能应用开发技术: 4,
    自然语言处理: 5,
    体育与健康4: 6,
    礼仪与沟通技巧: 7,
    数据结构: 8
  }
  return tones[item?.course] || 1
}
function courseDescription(course) {
  const map = {
    Python数据分析: '训练 Python 数据清洗、分析和可视化能力。',
    深度学习框架技术: '学习深度学习框架的模型训练和应用开发。',
    习近平新时代中国特色社会主义思想概论: '公共基础课程，学习新时代中国特色社会主义思想。',
    人工智能应用开发技术: '围绕 AI 应用项目开展接口、模型和业务开发训练。',
    自然语言处理: '学习文本处理、语义理解和智能问答等任务。',
    体育与健康4: '开展运动技能和健康管理训练。',
    礼仪与沟通技巧: '训练职业礼仪、表达和沟通协作能力。',
    数据结构: '学习基础数据结构与算法思维。'
  }
  return map[course] || '课程说明待补充。'
}
function openCourse(row) {
  selectedLesson.value = row
  courseVisible.value = true
}
async function studentLogin() {
  if (!loginForm.student_no || !loginForm.password) {
    ElMessage.warning('请输入学号和密码')
    return
  }
  loading.value = true
  try {
    const { data } = await studentHttp.post('/auth/student-login', loginForm)
    studentToken.value = data.access_token
    localStorage.setItem('student_token', studentToken.value)
    student.value = data.student
    ElMessage.success('登录成功')
    await loadStudentData()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
async function loadStudentData() {
  if (!studentToken.value) return
  try {
    const { data } = await studentHttp.get('/website/student/schedule')
    student.value = data.student
    schedules.value = data.schedules
    grades.value = data.grades
  } catch {
    logout()
  }
}
function logout() {
  studentToken.value = ''
  student.value = {}
  schedules.value = []
  grades.value = []
  localStorage.removeItem('student_token')
}
onMounted(loadStudentData)
</script>

<style scoped>
.schedule-page { min-height: 100vh; background: #f7f8fb; color: #172033; }
.mobile-head { display: grid; grid-template-columns: 64px 1fr 64px; align-items: center; padding: 20px 18px 14px; background: #fff; border-bottom: 1px solid #edf0f4; text-align: center; }
.back-btn,.logout-btn { border: 0; background: transparent; color: #202b35; }
.back-btn { font-size: 42px; line-height: 1; }
.logout-btn { font-size: 14px; }
.mobile-head p,.mobile-head h1 { margin: 0; }
.mobile-head p { color: #66716d; font-size: 18px; }
.mobile-head h1 { margin-top: 24px; font-size: 22px; font-weight: 500; }
.login-box { display: grid; min-height: calc(100vh - 106px); place-items: center; padding: 24px; }
.login-box .el-card { width: min(420px, 100%); }
.login-box h2 { margin: 0 0 8px; }
.login-box p { margin: 0 0 16px; color: #66716d; }
.login-box :deep(.el-input),.login-box .el-button { width: 100%; margin-top: 12px; }
.schedule-shell { max-width: 1180px; margin: 0 auto; background: #fff; }
.student-card { display: flex; justify-content: space-between; align-items: center; gap: 18px; padding: 18px; border-bottom: 1px solid #edf0f4; }
.student-card span { color: #0066b3; font-weight: 800; }
.student-card strong { display: block; margin-top: 4px; font-size: 24px; }
.student-card p { margin: 6px 0 0; color: #66716d; }
.week-bar { display: flex; align-items: center; justify-content: center; gap: 14px; padding: 16px 18px 10px; border-bottom: 1px solid #edf0f4; }
.week-bar h2,.week-bar p { margin: 0; text-align: center; }
.week-bar h2 { font-size: 28px; }
.week-bar p { margin-top: 6px; font-size: 18px; }
.class-row { display: flex; gap: 12px; padding: 12px 18px; }
.timetable-wrap { overflow-x: auto; }
.timetable { display: grid; grid-template-columns: 48px repeat(7, minmax(112px, 1fr)); grid-template-rows: 74px repeat(12, 56px); min-width: 840px; background: #eef2f5; }
.corner-cell,.day-head,.period-cell,.lesson-cell { position: relative; border-right: 1px solid #dde4ea; border-bottom: 1px solid #dde4ea; background: #fff; }
.day-head,.period-cell { display: grid; place-items: center; }
.day-head { gap: 2px; }
.day-head span { color: #56616b; font-size: 18px; }
.day-head strong { color: #2f627d; font-size: 22px; font-weight: 500; }
.period-cell { color: #9aa3aa; font-size: 20px; }
.lesson-card { position: absolute; z-index: 2; inset: 4px; height: calc(var(--span) * 56px - 8px); padding: 10px; border: 0; border-radius: 8px; text-align: left; color: #fff; overflow: hidden; }
.lesson-card strong,.lesson-card span { display: block; line-height: 1.28; }
.lesson-card strong { font-size: 18px; }
.lesson-card span { margin-top: 8px; font-size: 15px; }
.tone-1 { background: #8e91f4; } .tone-2 { background: #56b4f2; } .tone-3 { background: #b9e9e4; color: #356370; } .tone-4 { background: #bceee5; color: #27665d; } .tone-5 { background: #f0dba3; color: #7b5b15; } .tone-6 { background: #d8daf8; color: #55598b; } .tone-7 { background: #d6ebfb; color: #38627c; } .tone-8 { background: #f7d1cd; color: #8a3830; }
.grades-panel { padding: 18px; }
.panel-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-title h2 { margin: 0; }
.panel-title span { color: #66716d; }
.course-detail dl { display: grid; grid-template-columns: 72px 1fr; gap: 12px; margin-top: 18px; }
.course-detail dt { color: #66716d; }
.course-detail dd { margin: 0; }
@media (max-width: 720px) { .schedule-shell { max-width: none; } .week-bar { flex-wrap: wrap; } .student-card,.class-row { flex-direction: column; align-items: stretch; } }
</style>
