<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">ADMISSIONS CENTER</p>
        <h1>招生管理</h1>
        <p>维护专业库、历年分数、一分一段、智能匹配和报考建议书。</p>
      </div>
      <div class="actions">
        <el-button @click="exportExcel('majors')">导出专业</el-button>
        <el-button type="primary" @click="exportExcel('scores')">导出分数</el-button>
      </div>
    </section>

    <el-tabs v-model="tab" class="glass-tabs">
      <el-tab-pane label="专业库" name="majors">
        <el-card shadow="never" class="panel">
          <div class="toolbar">
            <el-input v-model="keyword" clearable placeholder="搜索专业名称" @change="loadMajors" />
            <el-upload :http-request="(opt) => importExcel('majors', opt)" :show-file-list="false">
              <el-button>导入专业 Excel</el-button>
            </el-upload>
          </div>
          <el-table :data="majors" stripe>
            <el-table-column prop="name" label="专业名称" min-width="170" />
            <el-table-column prop="college" label="所属学院" width="160" />
            <el-table-column prop="duration" label="学制" width="80" />
            <el-table-column prop="courses" label="核心课程" min-width="220" />
            <el-table-column prop="jobs" label="就业方向" min-width="240" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="录取分数" name="scores">
        <el-card shadow="never" class="panel">
          <div class="toolbar">
            <el-select v-model="selectedMajor" filterable placeholder="选择专业" @change="loadTrend">
              <el-option v-for="item in majors" :key="item.id" :label="item.name" :value="item.name" />
            </el-select>
            <el-input-number v-model="userScore" :min="0" :max="750" />
            <el-button type="primary" @click="loadRecommend">位次推荐</el-button>
            <el-upload :http-request="(opt) => importExcel('scores', opt)" :show-file-list="false">
              <el-button>导入分数</el-button>
            </el-upload>
            <el-upload :http-request="(opt) => importExcel('rank', opt)" :show-file-list="false">
              <el-button>导入一分一段</el-button>
            </el-upload>
          </div>

          <div v-if="trend.items?.length" class="trend-card">
            <h3>{{ trend.major }} 历年分数趋势</h3>
            <div v-for="item in trend.items" :key="item.year" class="bar-row">
              <span>{{ item.year }}</span>
              <div class="bar-track"><i :style="{ width: `${Math.min(100, item.min_score / 6)}%` }"></i></div>
              <b>最低 {{ item.min_score }} / 最高 {{ item.max_score }}</b>
            </div>
          </div>

          <el-alert v-if="recommend.rank" :title="`估算位次：${recommend.rank}`" type="success" show-icon />
          <el-table v-if="recommend.items" :data="recommend.items" stripe class="result-table">
            <el-table-column prop="major" label="推荐专业" />
            <el-table-column prop="level" label="等级" width="100" />
            <el-table-column prop="min_score" label="最低分" width="100" />
            <el-table-column prop="gap" label="分差" width="100" />
            <el-table-column prop="rank_min" label="往年最低位次" width="140" />
          </el-table>

          <el-table :data="scores" stripe class="result-table">
            <el-table-column prop="year" label="年度" width="90" />
            <el-table-column prop="major" label="专业" min-width="180" />
            <el-table-column prop="province" label="省份" width="90" />
            <el-table-column prop="subject" label="科类" width="90" />
            <el-table-column prop="min_score" label="最低分" width="100" />
            <el-table-column prop="max_score" label="最高分" width="100" />
            <el-table-column prop="enrollment" label="计划数" width="100" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="智能工具" name="tools">
        <el-row :gutter="18">
          <el-col :xs="24" :lg="12">
            <el-card shadow="never" class="panel">
              <h3>专业智能匹配问卷</h3>
              <el-form :model="matchForm" label-width="110px">
                <el-form-item label="兴趣领域">
                  <el-select v-model="matchForm.field">
                    <el-option label="算法" value="算法" />
                    <el-option label="数据" value="数据" />
                    <el-option label="硬件" value="硬件" />
                    <el-option label="应用开发" value="应用开发" />
                    <el-option label="交通工程" value="交通工程" />
                  </el-select>
                </el-form-item>
                <el-form-item label="职业类型">
                  <el-select v-model="matchForm.career">
                    <el-option label="研发" value="研发" />
                    <el-option label="分析" value="分析" />
                    <el-option label="产品" value="产品" />
                    <el-option label="运维" value="运维" />
                  </el-select>
                </el-form-item>
                <el-form-item label="数学接受度">
                  <el-select v-model="matchForm.math">
                    <el-option label="不怕" value="不怕" />
                    <el-option label="一般" value="一般" />
                    <el-option label="抵触" value="抵触" />
                  </el-select>
                </el-form-item>
                <el-form-item label="编程接受度">
                  <el-select v-model="matchForm.code">
                    <el-option label="热爱" value="热爱" />
                    <el-option label="能接受" value="能接受" />
                    <el-option label="不想写代码" value="不想写代码" />
                  </el-select>
                </el-form-item>
                <el-form-item label="读研计划">
                  <el-select v-model="matchForm.postgrad">
                    <el-option label="是" value="是" />
                    <el-option label="否" value="否" />
                  </el-select>
                </el-form-item>
                <el-button type="primary" @click="matchMajor">生成匹配报告</el-button>
              </el-form>
              <el-table v-if="matchResult.majors" :data="matchResult.majors" stripe class="result-table">
                <el-table-column prop="name" label="推荐专业" />
                <el-table-column prop="description" label="简介" />
                <el-table-column prop="jobs" label="就业方向" />
              </el-table>
            </el-card>
          </el-col>

          <el-col :xs="24" :lg="12">
            <el-card shadow="never" class="panel">
              <h3>专业对比与建议书</h3>
              <div class="toolbar">
                <el-select v-model="compareA" filterable placeholder="专业 A">
                  <el-option v-for="m in majors" :key="m.id" :label="m.name" :value="m.name" />
                </el-select>
                <el-select v-model="compareB" filterable placeholder="专业 B">
                  <el-option v-for="m in majors" :key="m.id" :label="m.name" :value="m.name" />
                </el-select>
                <el-button type="primary" @click="compareMajors">开始对比</el-button>
              </div>
              <el-table v-if="compareResult.items" :data="compareResult.items" stripe class="result-table">
                <el-table-column prop="name" label="专业" />
                <el-table-column prop="courses" label="课程" />
                <el-table-column prop="jobs" label="就业" />
                <el-table-column prop="avg_min_score" label="近三年均分" width="120" />
              </el-table>
              <el-divider />
              <el-input v-model="report.question" placeholder="咨询问题" />
              <el-input v-model="report.answer" type="textarea" :rows="4" placeholder="系统建议或老师建议" />
              <el-button type="primary" class="pdf-btn" @click="downloadReport">导出报考建议书 PDF</el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const tab = ref('majors')
const keyword = ref('')
const majors = ref([])
const scores = ref([])
const selectedMajor = ref('')
const trend = ref({})
const userScore = ref(430)
const recommend = ref({})
const matchForm = ref({ field: '算法', career: '研发', math: '一般', code: '能接受', postgrad: '否' })
const matchResult = ref({})
const compareA = ref('')
const compareB = ref('')
const compareResult = ref({})
const report = ref({ question: '', answer: '' })

async function loadMajors() {
  majors.value = (await http.get('/admissions/majors', { params: { keyword: keyword.value } })).data
}
async function loadScores() {
  scores.value = (await http.get('/admissions/scores')).data
}
async function loadTrend() {
  if (!selectedMajor.value) return
  trend.value = (await http.get('/admissions/scores/trend', { params: { major: selectedMajor.value } })).data
}
async function loadRecommend() {
  recommend.value = (await http.get('/admissions/recommend', { params: { score: userScore.value, subject: '物理' } })).data
}
async function importExcel(kind, options) {
  const data = new FormData()
  data.append('file', options.file)
  const res = await http.post(`/admissions/import/${kind}`, data)
  ElMessage.success(`导入成功：${res.data.count} 条`)
  await loadMajors()
  await loadScores()
}
function exportExcel(kind) {
  window.open(`/api/admissions/export/${kind}`, '_blank')
}
async function matchMajor() {
  matchResult.value = (await http.post('/admissions/match', matchForm.value)).data
}
async function compareMajors() {
  if (!compareA.value || !compareB.value) return ElMessage.warning('请选择两个专业')
  compareResult.value = (await http.get('/admissions/compare', { params: { a: compareA.value, b: compareB.value } })).data
}
async function downloadReport() {
  const res = await http.post('/admissions/report', report.value, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = '报考建议书.pdf'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  await loadMajors()
  selectedMajor.value = majors.value[0]?.name || ''
  compareA.value = majors.value[0]?.name || ''
  compareB.value = majors.value[1]?.name || ''
  await loadScores()
  await loadTrend()
})
</script>

<style scoped>
.page-head,
.panel,
.trend-card {
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
.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.toolbar {
  margin-bottom: 14px;
}
.toolbar .el-input {
  max-width: 320px;
}
.panel {
  margin-bottom: 18px;
}
.trend-card {
  padding: 18px;
  margin-bottom: 16px;
}
.bar-row {
  display: grid;
  grid-template-columns: 70px 1fr 190px;
  gap: 12px;
  align-items: center;
  margin: 10px 0;
}
.bar-track {
  height: 14px;
  border-radius: 999px;
  background: #edf2f7;
  overflow: hidden;
}
.bar-track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #91b51f, #19a56b);
}
.result-table {
  margin-top: 14px;
}
.pdf-btn {
  margin-top: 12px;
}
</style>
