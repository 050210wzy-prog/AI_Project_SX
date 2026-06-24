<template>
  <div class="dashboard">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">ADMIN OVERVIEW</p>
        <h1>学校一体化数据看板</h1>
        <p class="sub">汇总招生、官网内容、咨询工单、资源与 AI 反馈，帮助管理员快速发现待处理事项。</p>
      </div>
      <div class="hero-actions">
        <el-button v-if="isEmptyDashboard" type="success" :loading="seeding" @click="seedData">初始化基础数据</el-button>
        <el-button type="primary" @click="$router.push('/admin/admissions')">维护招生数据</el-button>
        <el-button @click="$router.push('/admin/website')">发布官网内容</el-button>
      </div>
    </section>

    <el-alert
      v-if="isEmptyDashboard"
      class="empty-alert"
      title="当前看板为 0，是因为数据库还没有写入专业、分数、文章等基础数据。点击“初始化基础数据”即可生成可管理的基础记录。"
      type="warning"
      show-icon
      :closable="false"
    />

    <el-row :gutter="18">
      <el-col v-for="item in cards" :key="item.key" :xs="24" :sm="12" :lg="6">
        <el-card class="metric" shadow="never">
          <div class="metric-title">
            <span>{{ item.label }}</span>
            <el-tag :type="item.type" effect="light">{{ item.desc }}</el-tag>
          </div>
          <b>{{ stats[item.key] || 0 }}</b>
          <small>{{ item.tip }}</small>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="18" class="charts">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="panel">
          <div class="panel-head">
            <h3>热门文章</h3>
            <el-button text @click="$router.push('/admin/website')">进入官网管理</el-button>
          </div>
          <div v-if="hotArticles.length" class="rank-list">
            <div v-for="(item, index) in hotArticles" :key="item.title" class="rank-row">
              <i>{{ String(index + 1).padStart(2, '0') }}</i>
              <span>{{ item.title }}</span>
              <b>{{ item.views }} 次</b>
            </div>
          </div>
          <el-empty v-else description="暂无浏览数据" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="panel">
          <div class="panel-head">
            <h3>工单状态</h3>
            <el-button text @click="$router.push('/admin/tickets')">处理工单</el-button>
          </div>
          <div v-if="ticketStatus.length" class="status-list">
            <div v-for="item in ticketStatus" :key="item.status" class="status-row">
              <span>{{ item.status }}</span>
              <el-progress :percentage="percent(item.count)" :stroke-width="12" />
              <b>{{ item.count }}</b>
            </div>
          </div>
          <el-empty v-else description="暂无工单" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="18" class="charts">
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="quick-card" @click="$router.push('/admin/students')">
          <h3>学生生命周期</h3>
          <p>档案、录取状态、班级分配、通知触达。</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="quick-card" @click="$router.push('/admin/academic')">
          <h3>教务运行</h3>
          <p>教师、课程、课表、成绩、考勤统一维护。</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="quick-card" @click="$router.push('/admin/settings')">
          <h3>系统治理</h3>
          <p>模型配置、权限、备份、安全审计与通知规则。</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const stats = ref({})
const seeding = ref(false)
const cards = [
  { key: 'majors', label: '专业数', desc: '招生基础', type: 'success', tip: '已纳入官网与招生推荐' },
  { key: 'scores', label: '分数记录', desc: '历年数据', type: 'primary', tip: '支持趋势与位次推荐' },
  { key: 'articles', label: '官网文章', desc: '门户内容', type: 'info', tip: '新闻、公告、专题栏目' },
  { key: 'pending_articles', label: '待审核文章', desc: '内容审核', type: 'warning', tip: '需编辑或审核员处理' },
  { key: 'pending_tickets', label: '待处理工单', desc: '咨询服务', type: 'danger', tip: '低置信度问答自动转入' },
  { key: 'resources', label: '资源文件', desc: '素材库', type: 'info', tip: '图片、附件、招生材料' },
  { key: 'feedback', label: 'AI 反馈', desc: '质量优化', type: 'warning', tip: '用于优化知识库与话术' }
]

const hotArticles = computed(() => stats.value.hot_articles || [])
const ticketStatus = computed(() => stats.value.ticket_status || [])
const totalTickets = computed(() => ticketStatus.value.reduce((sum, item) => sum + item.count, 0) || 1)
const percent = (count) => Math.round((count / totalTickets.value) * 100)
const isEmptyDashboard = computed(() => ['majors', 'scores', 'articles', 'pending_tickets', 'resources', 'feedback'].every((key) => !Number(stats.value[key] || 0)))

async function loadDashboard() {
  stats.value = (await http.get('/admin/dashboard')).data
}

async function seedData() {
  seeding.value = true
  try {
    const { data } = await http.post('/admin/dashboard/seed')
    await loadDashboard()
    ElMessage.success(`基础数据已初始化：专业 ${data.after.majors} 个，分数记录 ${data.after.scores} 条，文章 ${data.after.articles} 篇`)
  } finally {
    seeding.value = false
  }
}

onMounted(async () => {
  await loadDashboard()
})
</script>

<style scoped>
.dashboard {
  color: #101713;
}
.hero-panel,
.metric,
.panel,
.quick-card {
  border-radius: 24px;
  border: 1px solid rgba(16, 23, 19, .1);
  background: rgba(255,255,255,.78);
  box-shadow: 0 22px 55px rgba(24, 45, 39, .08);
}
.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
  margin-bottom: 18px;
}
.eyebrow {
  display: inline-flex;
  padding: 7px 12px;
  border: 1px solid rgba(16, 23, 19, .14);
  border-radius: 999px;
  font-weight: 800;
  font-size: 12px;
  letter-spacing: .08em;
  margin: 0 0 12px;
}
h1 {
  margin: 0;
  font-size: 34px;
}
.sub {
  max-width: 720px;
  color: #58635f;
}
.hero-actions {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}
.empty-alert {
  margin: -4px 0 18px;
}
.metric {
  margin-bottom: 18px;
}
.metric-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: #667085;
}
.metric b {
  display: block;
  margin-top: 12px;
  font-size: 40px;
}
.metric small {
  color: #7b8581;
}
.charts {
  margin-top: 4px;
}
.panel {
  min-height: 310px;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.panel h3,
.quick-card h3 {
  margin: 0;
}
.rank-row,
.status-row {
  display: grid;
  grid-template-columns: 42px 1fr 82px;
  gap: 14px;
  align-items: center;
  padding: 13px 0;
  border-bottom: 1px solid #edf0f4;
}
.rank-row i {
  font-style: normal;
  color: #94b322;
  font-weight: 900;
}
.status-row {
  grid-template-columns: 80px 1fr 42px;
}
.quick-card {
  cursor: pointer;
  min-height: 130px;
  transition: transform .2s ease, box-shadow .2s ease;
}
.quick-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 30px 70px rgba(24, 45, 39, .12);
}
.quick-card p {
  color: #66716d;
}
@media (max-width: 900px) {
  .hero-panel {
    flex-direction: column;
  }
}
</style>
