<template>
  <site-shell :breadcrumbs="[{ label: '智慧官网创新中心' }]">
    <section class="container innovation-hero">
      <div>
        <span>Smart Campus Web</span>
        <h1>智慧官网创新中心</h1>
        <p>围绕招生、专业、服务、数据、导览和英文官网，集中展示 8 个可交互创新功能。</p>
      </div>
      <aside>
        <b>8</b>
        <span>项创新已接入</span>
      </aside>
    </section>

    <section class="container innovation-nav">
      <button v-for="item in features" :key="item.key" type="button" @click="scrollTo(item.key)">
        <component :is="item.icon" />
        <span>{{ item.title }}</span>
      </button>
    </section>

    <section :id="features[0].key" class="container feature-section">
      <feature-heading index="01" title="招生智能推荐系统" desc="输入分数、科类和兴趣，自动生成冲稳保专业建议。" />
      <div class="recommend-layout">
        <div class="form-panel">
          <el-input v-model="recommendForm.province" placeholder="省份" />
          <el-select v-model="recommendForm.subject" placeholder="科类">
            <el-option label="物理" value="物理" />
            <el-option label="历史" value="历史" />
          </el-select>
          <el-input-number v-model="recommendForm.score" :min="150" :max="750" />
          <el-input v-model="recommendForm.interest" placeholder="兴趣方向，如 人工智能 / 轨道 / 汽车" />
          <el-button type="primary" :loading="loading.recommend" @click="loadRecommend">生成推荐</el-button>
        </div>
        <div class="result-grid">
          <article v-for="item in recommend.items" :key="item.major">
            <b :class="`level-${item.level}`">{{ item.level }}</b>
            <h3>{{ item.major }}</h3>
            <small>{{ item.college }} · 分差 {{ item.score_gap }}</small>
            <p>{{ item.reason }}</p>
          </article>
        </div>
      </div>
    </section>

    <section :id="features[1].key" class="container feature-section">
      <feature-heading index="02" title="专业画像页面" desc="把专业介绍升级为课程、岗位、证书、实训、企业和录取趋势的完整画像。" />
      <div class="profile-toolbar">
        <el-select v-model="selectedMajor" filterable placeholder="选择专业" @change="loadProfile">
          <el-option v-for="item in majors" :key="item.name" :label="item.name" :value="item.name" />
        </el-select>
        <el-button @click="openMajorPage">打开专业详情</el-button>
      </div>
      <div class="profile-layout">
        <article class="profile-main">
          <span>{{ profile.college }}</span>
          <h3>{{ profile.name }}</h3>
          <p>{{ profile.description }}</p>
          <div class="chip-row">
            <b v-for="item in profile.courses" :key="item">{{ item }}</b>
          </div>
        </article>
        <article>
          <h3>就业岗位</h3>
          <p v-for="item in profile.jobs" :key="item">{{ item }}</p>
        </article>
        <article>
          <h3>实训条件</h3>
          <p v-for="item in profile.training" :key="item">{{ item }}</p>
        </article>
        <article>
          <h3>合作企业</h3>
          <p v-for="item in profile.partners" :key="item">{{ item }}</p>
        </article>
      </div>
    </section>

    <section :id="features[2].key" class="container feature-section">
      <feature-heading index="03" title="官网内容自动同步与审核" desc="聚合后台文章、通知和图片状态，形成内容同步看板。" />
      <div class="sync-layout">
        <article v-for="item in sync.status" :key="item.name">
          <b>{{ item.count }}</b>
          <span>{{ item.name }}</span>
          <small>{{ item.state }}</small>
        </article>
      </div>
      <div class="list-panel">
        <button v-for="item in sync.latest" :key="item.id" type="button" @click="router.push(`/article/${item.id}`)">
          <time>{{ item.date }}</time>
          <span>{{ item.title }}</span>
        </button>
      </div>
    </section>

    <section :id="features[3].key" class="container feature-section">
      <feature-heading index="04" title="校园服务统一入口" desc="按学生、教师、考生、校友、访客不同身份聚合常用服务。" />
      <div class="role-tabs">
        <button v-for="role in roles" :key="role" type="button" :class="{ active: activeRole === role }" @click="changeRole(role)">
          {{ role }}
        </button>
      </div>
      <div class="service-grid">
        <article v-for="item in serviceDesk.apps" :key="item.title" @click="openService(item)">
          <component :is="Monitor" />
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </article>
      </div>
    </section>

    <section :id="features[4].key" class="container feature-section dark-section">
      <feature-heading index="05" title="可视化数据大屏" desc="集中展示官网、招生、咨询和服务数据。" inverse />
      <div class="analytics-cards">
        <article v-for="item in analytics.cards" :key="item.label">
          <b>{{ item.value }}</b>
          <span>{{ item.label }}</span>
        </article>
      </div>
      <div class="analytics-layout">
        <div>
          <h3>热门专业</h3>
          <p v-for="item in analytics.hot_majors" :key="item.major">{{ item.major }} · 平均最低分 {{ item.avg_score }}</p>
        </div>
        <div>
          <h3>热门文章</h3>
          <p v-for="item in analytics.hot_articles" :key="item.title">{{ item.title }} · {{ item.views }} 次</p>
        </div>
      </div>
    </section>

    <section :id="features[5].key" class="container feature-section">
      <feature-heading index="06" title="AI 招生问答增强版" desc="回答内容展示来源依据，提高招生问答可信度。" />
      <div class="ai-panel">
        <p>{{ aiSources.answer }}</p>
        <article v-for="item in aiSources.sources" :key="item.id" @click="router.push(`/article/${item.id}`)">
          <b>{{ item.channel }}</b>
          <span>{{ item.title }}</span>
          <small>{{ item.date }}</small>
        </article>
      </div>
    </section>

    <section :id="features[6].key" class="container feature-section">
      <feature-heading index="07" title="VR/地图式校园导览" desc="用交互地图思路展示校区、地点和交通指引。" />
      <div class="campus-layout">
        <article v-for="campus in campus.campuses" :key="campus.name">
          <h3>{{ campus.name }}</h3>
          <p>{{ campus.address }}</p>
          <div>
            <span v-for="spot in campus.spots" :key="spot">{{ spot }}</span>
          </div>
        </article>
      </div>
    </section>

    <section :id="features[7].key" class="container feature-section">
      <feature-heading index="08" title="英文官网自动内容映射" desc="中文内容进入英文官网草稿池，后续可由管理员审核发布。" />
      <div class="english-map">
        <article v-for="item in english.items" :key="item.zh_title">
          <b>{{ item.status }}</b>
          <h3>{{ item.en_title }}</h3>
          <p>{{ item.zh_title }}</p>
          <small>{{ item.channel }} · {{ item.date }}</small>
        </article>
      </div>
    </section>
  </site-shell>
</template>

<script setup>
import { defineComponent, h, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis, Files, Guide, MagicStick, Monitor, Reading, Search, Service } from '@element-plus/icons-vue'
import SiteShell from '../components/SiteShell.vue'
import http from '../api/http'

const router = useRouter()
const loading = reactive({ recommend: false })
const recommendForm = reactive({ province: '安徽', subject: '物理', score: 420, interest: '人工智能' })
const recommend = ref({ items: [] })
const majors = ref([])
const selectedMajor = ref('')
const profile = ref({ courses: [], jobs: [], training: [], partners: [] })
const sync = ref({ status: [], latest: [] })
const roles = ['学生', '教师', '考生', '校友', '访客']
const activeRole = ref('学生')
const serviceDesk = ref({ apps: [] })
const analytics = ref({ cards: [], hot_majors: [], hot_articles: [] })
const aiSources = ref({ sources: [] })
const campus = ref({ campuses: [] })
const english = ref({ items: [] })

const features = [
  { key: 'recommend', title: '招生推荐', icon: MagicStick },
  { key: 'profile', title: '专业画像', icon: Reading },
  { key: 'sync', title: '内容同步', icon: Files },
  { key: 'desk', title: '个人服务台', icon: Service },
  { key: 'analytics', title: '数据大屏', icon: DataAnalysis },
  { key: 'ai', title: 'AI 引用问答', icon: Search },
  { key: 'campus', title: '校园导览', icon: Guide },
  { key: 'english', title: '英文映射', icon: Monitor }
]

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
async function loadRecommend() {
  loading.recommend = true
  try {
    const { data } = await http.post('/innovation/recommend', recommendForm)
    recommend.value = data
  } finally {
    loading.recommend = false
  }
}
async function loadMajors() {
  const { data } = await http.get('/admissions/majors')
  majors.value = Array.isArray(data) ? data : []
  selectedMajor.value = majors.value[0]?.name || ''
  if (selectedMajor.value) await loadProfile()
}
async function loadProfile() {
  const { data } = await http.get(`/innovation/major-profile/${encodeURIComponent(selectedMajor.value)}`)
  profile.value = data
}
function openMajorPage() {
  if (profile.value.college) router.push(`/college/${encodeURIComponent(profile.value.college)}`)
}
async function changeRole(role) {
  activeRole.value = role
  const { data } = await http.get('/innovation/service-desk', { params: { role } })
  serviceDesk.value = data
}
function openService(item) {
  if (item.url?.startsWith('http')) window.open(item.url, '_blank')
  else router.push(item.url || `/service/${encodeURIComponent(item.title)}`)
}
async function loadAll() {
  await Promise.all([
    loadRecommend(),
    loadMajors(),
    http.get('/innovation/sync-center').then(({ data }) => (sync.value = data)),
    changeRole(activeRole.value),
    http.get('/innovation/analytics').then(({ data }) => (analytics.value = data)),
    http.get('/innovation/ai-sources').then(({ data }) => (aiSources.value = data)),
    http.get('/innovation/campus-guide').then(({ data }) => (campus.value = data)),
    http.get('/innovation/english-mapping').then(({ data }) => (english.value = data))
  ])
}

const FeatureHeading = defineComponent({
  props: { index: String, title: String, desc: String, inverse: Boolean },
  setup(props) {
    return () =>
      h('div', { class: ['feature-heading', props.inverse ? 'inverse' : ''] }, [
        h('span', props.index),
        h('div', [h('h2', props.title), h('p', props.desc)])
      ])
  }
})

onMounted(loadAll)
</script>

<style scoped>
.container {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
.innovation-hero {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 28px;
  align-items: end;
  margin-top: 24px;
  padding: 64px 52px;
  background:
    linear-gradient(120deg, rgba(0, 59, 112, .94), rgba(0, 102, 179, .86)),
    url("https://www.acvtc.edu.cn/images/nybanner_new.jpg") center / cover;
  color: #ffffff;
}
.innovation-hero span,
.feature-heading span {
  color: #9fe2ad;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.innovation-hero h1 {
  margin: 10px 0 14px;
  font-size: clamp(42px, 6vw, 72px);
}
.innovation-hero p {
  max-width: 720px;
  font-size: 20px;
  line-height: 1.75;
}
.innovation-hero aside {
  display: grid;
  place-items: center;
  min-height: 180px;
  border: 1px solid rgba(255, 255, 255, .36);
  background: rgba(255, 255, 255, .14);
}
.innovation-hero aside b {
  font-size: 76px;
  line-height: 1;
}
.innovation-nav {
  position: sticky;
  top: 0;
  z-index: 8;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  padding: 14px 0;
  background: #f5f7fa;
}
.innovation-nav button,
.role-tabs button {
  border: 1px solid #dce5ee;
  background: #ffffff;
  color: #003b70;
  padding: 12px 10px;
  cursor: pointer;
  font-weight: 800;
}
.innovation-nav svg {
  width: 20px;
  height: 20px;
  margin-right: 4px;
  vertical-align: -5px;
}
.feature-section {
  scroll-margin-top: 78px;
  margin-top: 26px;
  padding: 34px;
  border: 1px solid #dce5ee;
  background: #ffffff;
  box-shadow: 0 18px 42px rgba(0, 54, 96, .07);
}
.dark-section {
  background: #003b70;
  color: #ffffff;
}
.feature-heading {
  display: grid;
  grid-template-columns: 82px 1fr;
  gap: 18px;
  margin-bottom: 24px;
}
.feature-heading span {
  color: #c41e3a;
  font-size: 28px;
}
.feature-heading h2 {
  margin: 0 0 8px;
  color: #003b70;
  font-size: 34px;
}
.feature-heading p {
  margin: 0;
  color: #5f6c78;
}
.feature-heading.inverse h2,
.feature-heading.inverse p {
  color: #ffffff;
}
.recommend-layout,
.profile-layout,
.analytics-layout,
.campus-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
}
.form-panel {
  display: grid;
  gap: 12px;
  align-content: start;
  padding: 20px;
  background: #f5f7fa;
  border-left: 4px solid #0066b3;
}
.result-grid,
.service-grid,
.english-map,
.sync-layout {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
article,
.ai-panel article,
.list-panel button {
  border: 1px solid #dce5ee;
  background: #fbfdff;
  padding: 18px;
}
article h3 {
  margin: 8px 0;
  color: #003b70;
}
article p,
article small,
.ai-panel p,
.list-panel span {
  color: #5f6c78;
  line-height: 1.7;
}
.result-grid b {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  color: #ffffff;
  background: #0066b3;
}
.level-保 {
  background: #2e7d32 !important;
}
.level-冲 {
  background: #c41e3a !important;
}
.level-慎报 {
  background: #7a8694 !important;
}
.profile-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.profile-toolbar .el-select {
  width: min(420px, 100%);
}
.profile-main {
  grid-row: span 3;
  background: linear-gradient(160deg, #f7fbff, #eef8f1);
}
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip-row b,
.campus-layout span {
  padding: 7px 10px;
  color: #0066b3;
  background: #edf5fb;
}
.sync-layout article b,
.analytics-cards b {
  display: block;
  color: #0066b3;
  font-size: 38px;
}
.list-panel {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}
.list-panel button {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 16px;
  cursor: pointer;
  text-align: left;
}
.role-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.role-tabs button.active,
.innovation-nav button:hover {
  color: #ffffff;
  background: #0066b3;
}
.service-grid article {
  cursor: pointer;
}
.service-grid svg {
  width: 30px;
  height: 30px;
  color: #2e7d32;
}
.analytics-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}
.analytics-cards article,
.analytics-layout > div {
  border-color: rgba(255, 255, 255, .18);
  background: rgba(255, 255, 255, .08);
}
.analytics-cards b,
.analytics-layout h3,
.analytics-layout p {
  color: #ffffff;
}
.ai-panel {
  display: grid;
  gap: 12px;
}
.ai-panel article {
  display: grid;
  grid-template-columns: 110px 1fr 110px;
  gap: 14px;
  cursor: pointer;
}
.campus-layout {
  grid-template-columns: repeat(2, 1fr);
}
.campus-layout div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
@media (max-width: 980px) {
  .innovation-hero,
  .recommend-layout,
  .profile-layout,
  .analytics-layout {
    grid-template-columns: 1fr;
  }
  .innovation-nav,
  .result-grid,
  .service-grid,
  .english-map,
  .sync-layout,
  .analytics-cards,
  .campus-layout {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 680px) {
  .container {
    width: min(100vw - 22px, 1180px);
  }
  .feature-section,
  .innovation-hero {
    padding: 24px;
  }
  .innovation-nav,
  .result-grid,
  .service-grid,
  .english-map,
  .sync-layout,
  .analytics-cards,
  .campus-layout,
  .ai-panel article {
    grid-template-columns: 1fr;
  }
}
</style>
