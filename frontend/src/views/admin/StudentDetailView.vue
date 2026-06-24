<template>
  <div class="student-detail">
    <section class="detail-head">
      <div>
        <el-button text @click="$router.push('/admin/students')">返回学生管理</el-button>
        <h1>{{ student?.name || '学生档案' }}</h1>
        <p>{{ student?.major }} / {{ student?.className }} / {{ student?.examNo }}</p>
      </div>
      <el-tag v-if="student" :type="statusType(student.status)" size="large">{{ student.status }}</el-tag>
    </section>

    <el-skeleton v-if="loading" :rows="8" animated />
    <template v-else-if="student">
      <section class="metric-grid">
        <div v-for="item in cards" :key="item.label" class="metric">
          <span>{{ item.label }}</span>
          <b>{{ item.value || '-' }}</b>
        </div>
      </section>

      <section class="sections">
        <detail-card title="基本信息" :items="basicItems" />
        <detail-card title="录取信息" :items="admissionItems" />
        <detail-card title="联系方式" :items="contactItems" />
        <detail-card title="投档成绩与志愿" :items="scoreItems" />
      </section>

      <section class="link-grid">
        <el-card shadow="never" class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">TIMETABLE</p>
              <h3>本班课表</h3>
            </div>
            <el-button @click="$router.push('/admin/academic')">进入教务管理</el-button>
          </div>
          <el-table :data="academic.schedules" stripe>
            <el-table-column prop="day" label="星期" width="72" />
            <el-table-column prop="time" label="节次" width="90" />
            <el-table-column prop="course" label="课程" min-width="140" />
            <el-table-column prop="teacher" label="教师" width="100" />
            <el-table-column prop="room" label="教室" width="120" />
            <el-table-column label="状态" width="96">
              <template #default="{ row }">
                <el-tag :type="row.status === '已发布' ? 'success' : 'warning'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="never" class="panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">GRADES</p>
              <h3>成绩与考核</h3>
            </div>
            <el-tag :type="gradeWarningCount ? 'warning' : 'success'">{{ gradeWarningCount ? `${gradeWarningCount} 项预警` : '状态正常' }}</el-tag>
          </div>
          <el-table :data="academic.grades" stripe>
            <el-table-column prop="course" label="课程" min-width="150" />
            <el-table-column prop="processScore" label="平时" width="70" />
            <el-table-column prop="finalScore" label="期末" width="70" />
            <el-table-column prop="practiceScore" label="实训" width="70" />
            <el-table-column prop="totalScore" label="总评" width="78">
              <template #default="{ row }">
                <strong :class="['score-pill', { danger: row.totalScore < 60 }]">{{ row.totalScore }}</strong>
              </template>
            </el-table-column>
            <el-table-column label="出勤" width="112">
              <template #default="{ row }">
                <el-progress :percentage="row.attendance" :stroke-width="8" />
              </template>
            </el-table-column>
            <el-table-column prop="assessment" label="考核方式" width="112" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '正常' ? 'success' : 'warning'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </section>

      <el-card shadow="never" class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">NOTICE</p>
            <h3>通知记录</h3>
          </div>
          <el-button type="primary" @click="sendNotice">发送通知</el-button>
        </div>
        <el-empty v-if="!notices.length" description="暂无通知记录" />
        <el-timeline v-else>
          <el-timeline-item v-for="item in notices" :key="item.id" :timestamp="item.time">
            <strong>{{ item.title }}</strong>
            <p>{{ item.content }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const route = useRoute()
const loading = ref(true)
const student = ref(null)
const notices = ref([])
const academic = ref({ schedules: [], grades: [] })
const statusType = (value) => ({ 已报到: 'success', 已录取: 'primary', 待确认: 'warning', 需补材料: 'danger' }[value] || 'info')

const cards = computed(() => [
  { label: '学号', value: student.value?.student_no },
  { label: '投档成绩', value: student.value?.score },
  { label: '辅导员', value: student.value?.counselor },
  { label: '联系电话', value: student.value?.phone }
])
const basicItems = computed(() => [
  ['姓名', student.value?.name],
  ['性别', student.value?.gender],
  ['身份证号', student.value?.id_card],
  ['出生年月', student.value?.birthday],
  ['政治面貌', student.value?.political_status],
  ['民族', student.value?.ethnicity]
])
const admissionItems = computed(() => [
  ['考生号', student.value?.examNo],
  ['学号', student.value?.student_no],
  ['院系', student.value?.department],
  ['班级', student.value?.className],
  ['录取专业', student.value?.major],
  ['专业代码', student.value?.major_code],
  ['录取方式', student.value?.admission_type],
  ['录取批次', student.value?.admission_batch],
  ['科类', student.value?.subject || student.value?.subject_name]
])
const contactItems = computed(() => [
  ['省份', student.value?.province],
  ['城市', student.value?.city],
  ['地区代码', student.value?.area_code],
  ['地区名称', student.value?.area_name],
  ['家庭地址', student.value?.address],
  ['邮政编码', student.value?.postal_code],
  ['收件人', student.value?.receiver],
  ['联系电话', student.value?.phone]
])
const scoreItems = computed(() => [
  ['投档成绩', student.value?.score],
  ['投档志愿', student.value?.application_choice],
  ['填报专业1', student.value?.first_major],
  ['填报专业2', student.value?.second_major],
  ['填报专业3', student.value?.third_major],
  ['是否调剂', student.value?.adjustment],
  ['语文', student.value?.chinese_score],
  ['数学', student.value?.math_score],
  ['外语', student.value?.foreign_score],
  ['综合', student.value?.comprehensive_score]
])
const gradeWarningCount = computed(() => academic.value.grades.filter((item) => item.totalScore < 60 || item.attendance < 80 || item.status !== '正常').length)

const DetailCard = defineComponent({
  props: { title: String, items: Array },
  setup(props) {
    return () =>
      h('el-card', { shadow: 'never', class: 'panel' }, () => [
        h('h3', props.title),
        h('dl', { class: 'detail-list' }, props.items.map(([label, value]) => [
          h('dt', label),
          h('dd', value || '-')
        ]).flat())
      ])
  }
})

async function load() {
  loading.value = true
  const [studentRes, noticeRes] = await Promise.all([
    http.get('/admin/students'),
    http.get('/admin/admin-notices')
  ])
  student.value = studentRes.data.find((item) => String(item.id) === String(route.params.id))
  notices.value = noticeRes.data.filter((item) => item.target === student.value?.name)
  if (student.value?.id) {
    const { data } = await http.get(`/admin/students/${student.value.id}/academic`)
    academic.value = data
  }
  loading.value = false
}

async function sendNotice() {
  await http.post(`/admin/students/${student.value.id}/notice`)
  ElMessage.success('通知已发送并记录')
  await load()
}

onMounted(load)
</script>

<style scoped>
.student-detail {
  color: #1f2a2f;
}

.detail-head,
.panel,
.metric {
  border: 1px solid #e1e8ee;
  border-radius: 8px;
  background: #fff;
}

.detail-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  padding: 26px;
  margin-bottom: 18px;
  background: linear-gradient(135deg, #f8fbff 0%, #eef8f3 100%);
}

h1 {
  margin: 8px 0;
  font-size: 34px;
}

.detail-head p {
  margin: 0;
  color: #66716d;
}

.metric-grid,
.sections,
.link-grid {
  display: grid;
  gap: 18px;
  margin-bottom: 18px;
}

.metric-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.sections,
.link-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric {
  padding: 18px;
}

.metric span {
  color: #66716d;
}

.metric b {
  display: block;
  margin-top: 8px;
  color: #003b6f;
  font-size: 24px;
}

.panel {
  margin-bottom: 18px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #0066b3;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
}

.detail-list {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 12px 16px;
}

.detail-list dt {
  color: #66716d;
}

.detail-list dd {
  margin: 0;
  color: #17211d;
  font-weight: 700;
  word-break: break-word;
}

.score-pill {
  display: inline-grid;
  min-width: 48px;
  height: 28px;
  place-items: center;
  border-radius: 8px;
  background: #eef8f3;
  color: #2e7d32;
}

.score-pill.danger {
  background: #fff1f1;
  color: #c41e3a;
}

@media (max-width: 1000px) {
  .metric-grid,
  .sections,
  .link-grid {
    grid-template-columns: 1fr;
  }
}
</style>
